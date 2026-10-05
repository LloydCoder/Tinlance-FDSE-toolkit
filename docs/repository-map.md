# Repository Reconstruction Map

| Historical component | Forensic location | Target ownership |
|---|---|---|
| Report Generator | legacy/v1_components/report_generator.py | src/fdse_toolkit/reporting/ |
| GUI launcher | legacy/v1_components/toolkit_gui.py | src/fdse_toolkit/cli.py and field UI tooling |
| Air-gap builder | legacy/v1_components/build_airgap_bundle.py | src/fdse_toolkit/airgap/ |
| IR Playbook | legacy/new_components/ir_playbook/ir_playbook.py | src/fdse_toolkit/playbooks/ |
| ROI Calculator | legacy/new_components/roi_calculator/roi_calculator.py | src/fdse_toolkit/roi/ |
| Identity Scanner | legacy/new_components/identity_scanner/identity_scanner.py | src/fdse_toolkit/identity/ |
| Remote Delivery | legacy/new_components/remote_portal/remote_delivery.py | src/fdse_toolkit/delivery/ |
| Binary Builder | legacy/new_components/binaries/build_binaries.py | packaging/ and release tooling |

The legacy tree is forensic reference. Target modules must not silently copy unverified claims or insecure behavior.
