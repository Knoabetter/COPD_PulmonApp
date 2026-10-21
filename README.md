\# PulmonApp



A web application for spirometry analysis (COPD), built together with the Pulmonary Institute at Ichilov Hospital as a final project for a B.Sc. in Biomedical Engineering at Tel Aviv University.



\## What it does

\- A scanned spirometry report is uploaded as a PDF and the values are extracted with OCR.

\- Reference values are calculated with the GLI 2012 and the Murray equations and shown side by side.

\- A physician-notes panel (category dropdowns and quick-insert phrases) builds an editable note.

\- The application has two modules: clinical support, and database management (still in development).



\## Status and known limitations

\- The project is in the process of integration with Ichilov and is not in clinical use.

\- The final report (`COPD Project Paper/Final Report/Final\_Report\_COPD.pdf`) describes the version submitted in August 2025. The calculator and extraction code have changed since then, so details in the report (for example how Murray and GLI results are classified) may not match the current code. The code is the current source of truth.

\- Known extraction issues at the time of the last test run: on some old-format reports, a double decimal point (for example 3.4.3) can leave FVC empty; on the new-format reports tested, FVC was filled for 12 of 13 files and FEV1 was left blank on 9 of 13.

\- The hospital has a new spirometry machine whose report layout is not yet supported; new extraction patterns are needed.

\- The Murray vs GLI comparison was a small demo on 34 patients, not a validation study.

\- Benchmark helper scripts (a batch runner that does not write to the database, and a script that compares batch result files) are kept locally and are not included in this repository.

\- No patient data is included in this repository. Real reports used for testing are kept outside it.

