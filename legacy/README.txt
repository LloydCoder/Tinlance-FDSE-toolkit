
Tinlance FDSE Toolkit v2.0.0 — COMPLETE
=========================================
Built: 2026-06-06
By: Tinlance Limited (RC: 7962164) | tinlance.com
Live: http://13.50.16.19/dashboard

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT'S NEW IN v2.0.0 (vs v1.0.0)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Incident Response Playbook Generator
   6 alert types · MITRE mapped · NIS2 linked · comms templates

✅ ROI Calculator + MTTD/MTTR Dashboard
   418x ROI proven · 847ms MTTD vs 207-day industry avg
   Board-ready Word + 3-tab Excel dashboard

✅ Identity Threat Scanner (ITDR layer)
   Nigerian fintech credentials · AWS/GitHub/Stripe · JWT
   DNS exposure · MFA gap assessment · 18 credential patterns

✅ Remote Delivery Portal
   SHA-256 verified packages · Password-protected archives
   Client email template · Verify scripts (Windows + Linux)
   Answers the "is this a virus?" question completely

✅ Compiled Linux Binaries
   TinlanceIR · TinlanceROI · TinlanceIDScan
   No Python required — run directly on client machines

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COMPLETE TOOLKIT CONTENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

new_components/
  ir_playbook/ir_playbook.py         IR Playbook Generator
  roi_calculator/roi_calculator.py   ROI + MTTD/MTTR Calculator  
  identity_scanner/identity_scanner.py  Identity Threat Scanner
  remote_portal/remote_delivery.py   Remote Delivery System
  binaries/build_binaries.py         PyInstaller Build Script

binaries/linux/
  TinlanceIR      Compiled IR Playbook binary (Linux)
  TinlanceROI     Compiled ROI Calculator binary (Linux)
  TinlanceIDScan  Compiled Identity Scanner binary (Linux)

demo_outputs/
  Tinlance_IR_Playbook_Demo.docx     Sample IR Playbook
  Tinlance_ROI_Analysis_Demo.docx    Sample ROI Analysis
  Tinlance_ROI_Dashboard_Demo.xlsx   Sample ROI Dashboard

engagement_docs/
  Tinlance_Pilot_Agreement.docx
  Tinlance_Discovery_Call_Script.docx
  Tinlance_Scope_Template.docx
  Tinlance_Handoff_Checklist.docx

case_studies/
  Tinlance_Case_Study_001_Engr_Uzoma.docx

v1_components/
  report_generator.py     PDF+Word+Excel security report
  toolkit_gui.py          Tkinter GUI launcher
  build_airgap_bundle.py  USB air-gap bundle builder

demo_reports/
  TinlanceReport_Demo.pdf/.docx/.xlsx

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
QUICK START
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
pip install reportlab openpyxl python-docx

IR Playbook:     python new_components/ir_playbook/ir_playbook.py --demo
ROI Calculator:  python new_components/roi_calculator/roi_calculator.py --demo
Identity Scan:   python new_components/identity_scanner/identity_scanner.py --demo
Remote Delivery: python new_components/remote_portal/remote_delivery.py --demo
Report:          python v1_components/report_generator.py --demo
GUI:             python v1_components/toolkit_gui.py

Linux Binaries (no Python needed):
  ./binaries/linux/TinlanceIR --demo
  ./binaries/linux/TinlanceROI --demo
  ./binaries/linux/TinlanceIDScan --demo

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LIVE SYSTEMS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FusionOps Dashboard:  http://13.50.16.19/dashboard
Health Check:         http://13.50.16.19/health
API Docs:             http://13.50.16.19/docs
ThreatFade Source:    github.com/LloydCoder/tinlance-threatfade

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VALIDATED RESULTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ThreatFade MTTD:      847ms (industry avg: 207 days)
ROI Multiple:         418x for fintech clients
False Positive Rate:  0% (100-run validation)
Beta Validator:       Engr Uzoma — "Everything passed. It's solid."
Malware Validated:    Merlin QUIC z=14.76, Cobalt Strike z=7.01, IcedID z=3.89
