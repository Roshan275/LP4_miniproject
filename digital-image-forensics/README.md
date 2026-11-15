# PixelProof — Digital Image Forensic Analysis Tool

PixelProof is a local web application for a Cyber Security and Digital Forensics miniproject. It examines an image using four complementary techniques and presents visual maps plus a text report:

- **Metadata extraction:** EXIF tags, image/file details, SHA-256 hash, and a GPS presence indicator. GPS coordinates are intentionally withheld from the page.
- **Error Level Analysis (ELA):** recompresses the image as JPEG and amplifies pixel differences for visual inspection.
- **Noise consistency:** measures high-frequency residuals in image regions and creates a heatmap.
- **Copy-move candidates:** uses ORB feature descriptors to find visually similar features separated in the image.
- **Evidence Integrity Report:** downloads a print-ready HTML report with the original filename, dimensions, SHA-256 hash, analysis summaries, and report timestamp. It opens in a browser or Word and can be printed to PDF.

The app uses Python, Flask, Pillow, OpenCV, NumPy, and ExifRead. It runs locally; uploaded files stay in the project's ignored `instance/uploads/` directory. No database or external analysis service is used.

## Requirements

- Python 3.10 or newer (the report specifies Python 3.8+; this implementation uses modern type annotations)
- pip
- A modern browser

## Run on macOS or Linux

```bash
cd digital-image-forensics
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python app.py
```

Open <http://127.0.0.1:5000>, choose an image, and select **Analyze image**. Stop the server with `Ctrl+C`. On Windows, activate the environment with `.venv\\Scripts\\activate` instead of the `source` command.

## Project layout

```text
digital-image-forensics/
├── app.py                 # Flask routes, uploads, EXIF report and ELA
├── forensic.py            # Noise and copy-move heuristic analysis
├── templates/index.html   # Upload page and analysis report
├── static/style.css       # Responsive interface
├── requirements.txt
└── .gitignore             # Excludes local uploads and Python artifacts
```

## Run the automated tests

Install dependencies as above, then run:

```bash
python -m pytest
```

The tests generate a deterministic JPEG in memory and use a temporary upload directory. They cover a successful upload and report, missing/unsupported/corrupt files, upload and pixel-dimension limits, valid PNG responses from the ELA, noise, and copy-move image endpoints, and the downloadable evidence report. The dimension-limit test substitutes image dimensions instead of allocating a 40-megapixel fixture.

## GitHub

From the repository root, add and commit this folder. `.venv`, Python cache files, and uploaded evidence are ignored. Keep `requirements.txt` and `README.md` in Git. Do not commit sensitive evidence images or their reports unless you have authorization to share them.

## Important limitations

This project is an educational triage aid, not an authenticity certifier or a substitute for a forensic examiner. ELA, noise statistics, and feature matching can produce false positives and false negatives. JPEG recompression can make native PNG or other formats appear different, repeated natural textures can trigger copy-move matches, and an absence of indicators does not prove an image is genuine. Preserve the original evidence, document its chain of custody, and corroborate findings with other methods. The upload limit is 20 MB and the image dimension limit is 40 megapixels.

The downloadable report is a convenient record of the analysis, not a digital signature or a complete chain-of-custody system. It does not prove who submitted the image or that it remained unchanged outside this application. Open the downloaded HTML report in Word to save a DOCX copy, or use the browser's Print command to save it as PDF.

## Report mapping

The implementation covers the report's requested metadata extraction, ELA, noise inconsistency, copy-move analysis, visual and textual output, modular organization, and image-input validation. Matplotlib and Pandas are not needed by this implementation: OpenCV creates the visual maps and the report is rendered directly in the browser. Tkinter is not needed because Flask provides the user interface. Automated accuracy claims require a labeled genuine/manipulated image dataset and ground truth; the app does not present heuristic scores as proof.
