---
name: esf-audit-verification
description: >-
  Audits, tests, and verifies ESF+ compliance data in Competence 5.0 LMS.
  Use when validating participant Digital IDs, recalculating HMAC checksums,
  checking audit log completeness, or testing the ESF+ reporting pack exports.
---

# ESF+ Audit Verification & Integrity Checking

This skill provides step-by-step instructions for testing and validating ESF+ compliance across the Competence 5.0 LMS.

## Audit Workflow

### 1. Verify Digital ID Integrity
To detect if any participant records have suffered unauthorized SQL modifications or missing checksums:

```bash
docker compose exec web php -r "
define('CLI_SCRIPT', true);
require('config.php');
\$records = \$DB->get_records('local_digitalid');
\$tampered = 0;
foreach (\$records as \$r) {
    if (!\local_digitalid\digitalid_manager::verify_integrity(\$r)) {
        echo 'TAMPER ALERT: User ID ' . \$r->userid . ' (Digital ID: ' . \$r->digitalid . ')\n';
        \$tampered++;
    }
}
if (\$tampered === 0) {
    echo 'ALL ' . count(\$records) . ' DIGITAL IDS VERIFIED CLEAN.\n';
}
"
```

Shortcut:
```bash
make test-audit
```

### 2. Verify Audit Log Coverage
Ensure that every user registered in the system has a corresponding entry in `local_digitalid_audit`:

```bash
docker compose exec web php -r "
define('CLI_SCRIPT', true);
require('config.php');
\$users = \$DB->get_records_select('user', 'id > 1 AND deleted = 0');
foreach (\$users as \$u) {
    \$has_did = \$DB->record_exists('local_digitalid', ['userid' => \$u->id]);
    \$has_log = \$DB->record_exists('local_digitalid_audit', ['userid' => \$u->id, 'action' => 'registration']);
    if (\$has_did && !\$has_log) {
        echo 'COMPLIANCE GAP: User ' . \$u->id . ' (' . \$u->email . ') missing registration audit entry.\n';
    }
}
echo 'AUDIT LOG COVERAGE VERIFICATION COMPLETE.\n';
"
```

### 3. Test Export Streaming Endpoints (CLI)
Verify that the reporting export controller produces non-empty CSV output across all 4 reports:

```bash
# Test Participant Register Export
docker compose exec web php -r "define('CLI_SCRIPT', true); require('config.php'); ob_start(); \local_esf_export\reporter::stream_participant_register(0);" | head -n 5

# Test Activity Evidence Export
docker compose exec web php -r "define('CLI_SCRIPT', true); require('config.php'); ob_start(); \local_esf_export\reporter::stream_activity_evidence(0);" | head -n 5

# Test Session Attendance Export
docker compose exec web php -r "define('CLI_SCRIPT', true); require('config.php'); ob_start(); \local_esf_export\reporter::stream_attendance_lists(0);" | head -n 5

# Test Cohort Summary Export
docker compose exec web php -r "define('CLI_SCRIPT', true); require('config.php'); ob_start(); \local_esf_export\reporter::stream_cohort_summary(0);" | head -n 5
```
