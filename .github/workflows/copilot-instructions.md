{
  "copilot": {
    "role": "expert_qa_python_django",
    "objective": "Generate and fix pytest tests that pass on first execution, without manual intervention.",
    "project_structure": {
      "source_root": "backend/",
      "tests_root": "tests/",
      "test_layout_rule": "mirror_structure",
      "examples": {
        "backend/accounting/views/treasury.py": "tests/accounting/views/test_treasury.py",
        "backend/accounting/views/journal_entries.py": "tests/accounting/views/test_journal_entries.py",
        "backend/services/payment.py": "tests/services/test_payment.py",
        "backend/views/invoice.py": "tests/views/test_invoice.py"
      }
    },
    "test_generation": {
      "framework": "pytest",
      "django_plugin": "pytest-django",
      "mocking": "pytest-mock",
      "forbidden": [
        "unittest.TestCase",
        "django.test.TestCase",
        "APITestCase"
      ]
    },
    "naming_convention": {
      "test_function_pattern": "test_<function_name>_<explicit_scenario>",
      "allowed_scenarios": [
        "success",
        "unauthenticated",
        "invalid_data",
        "edge_case",
        "raises_exception"
      ],
      "rules": [
        "Scenario name must be explicit", "No vague or implicit test names"
      ]
    },
    "coverage_rules": {
      "minimum_per_unit": [
        "success_case",
        "business_error_case",
        "realistic_edge_case"
      ],
      "skip_rule": "If a scenario is not applicable, explain why and do not invent it"
    },
    "assertions": {
      "requirements": [
        "explicit",
        "deterministic",
        "no_external_dependency"
      ],
      "forbidden_patterns": [
        "assert response",
        "assert obj",
        "time_dependent_assertions",
        "order_dependent_assertions"
      ]
    },
    "django_rules": {
      "authentication": {
        "mandatory": true,
        "rules": [
          "Always create a user explicitly using an existing fixture or factory",
          "Always set request.user = user",
          "Never assume implicit authentication"
        ]
      },
      "http_requests": {
        "factory": [
          "RequestFactory",
          "APIRequestFactory"
        ],
        "mandatory_fields": [
          "request.method",
          "request.user",
          "request.data or request.POST"
        ]
      }
    },
    "database_rules": {
      "django_db_marker": {
        "mandatory_if_db_accessed": true,
        "rule": "Never access ORM without @pytest.mark.django_db"
      },
      "forbidden": [
        "mocking_django_orm_without_reason",
        "implicit_database_access"
      ]
    },
    "fixtures_policy": {
      "golden_rule": "Never invent fixtures",
      "verification_steps": [
        "Check conftest.py",
        "Check pytest --fixtures output"
      ],
      "if_fixture_missing": [
        "Create explicit local fixture",
        "Or use an existing verified fixture"
      ],
      "forbidden_patterns": [
        "assumed *_factory fixtures",
        "implicit fixtures",
        "undeclared fixtures"
      ]
    },
    "mocking_rules": {
      "method": "mocker.patch",
      "requirements": [
        "Patch the real import path used by the code",
        "Do not patch the tested module by default"
      ],
      "cleanup": "Handled automatically by pytest"
    },
    "vscode_compatibility": {
      "required_commands": [
        "pytest <file>",
        "pytest tests/",
        "pytest --cov=. --cov-report=html"
      ],
      "forbidden": [
        "absolute_paths",
        "implicit_dependencies",
        "execution_order_dependency"
      ]
    },
    "auto_correction_policy": {
      "on_test_failure": [
        "Read full pytest error message",
        "Identify exact root cause (auth, fixture, mock, import, db)",
        "Fix the test before responding",
        "Never return a failing test"
      ],
      "setup_error_rule": "A setup error invalidates the test"
    },
    "expected_result": {
      "first_run_success": true,
      "maintainable": true,
      "no_manual_copy_paste": true,
      "ci_ready": true
    }
  }
}
