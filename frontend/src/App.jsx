import { useState } from "react";
import "./App.css";

const API_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
function App() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFile = (selectedFile) => {
  if (!selectedFile) {
    return;
  }

  const allowedTypes = [
    "image/png",
    "image/jpeg",
    "image/webp",
  ];

  if (!allowedTypes.includes(selectedFile.type)) {
    setError(
      "Unsupported file type. Please upload a PNG, JPG, or WEBP image."
    );
    return;
  }

  setFile(selectedFile);
  setPreview(URL.createObjectURL(selectedFile));
  setResult(null);
  setError(null);
};

const handleFileChange = (event) => {
  handleFile(event.target.files[0]);
};

const handleDragOver = (event) => {
  event.preventDefault();
  event.stopPropagation();

  setDragActive(true);
};

const handleDragLeave = (event) => {
  event.preventDefault();
  event.stopPropagation();

  setDragActive(false);
};

const handleDrop = (event) => {
  event.preventDefault();
  event.stopPropagation();

  setDragActive(false);

  const droppedFile = event.dataTransfer.files[0];

  handleFile(droppedFile);
};
  const analyzeLabel = async () => {
    if (!file) {
      setError("Please select a label image first.");
      return;
    }

    setAnalyzing(true);
    setError(null);
    setResult(null);

    const formData = new FormData();

    formData.append("file", file);

    try {
      const response = await fetch(
        `${API_URL}/analyze`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(
          data.error || "Unable to analyze the label."
        );
      }

      setResult(data);

    } catch (err) {
      setError(err.message);
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="app">

      {/* Header */}
      <header className="header">
        <div>
          <h1>TTB Label Verifier</h1>
          <p>AI-Powered Alcohol Label Verification</p>
        </div>

        <div className="header-badge">
          Prototype
        </div>
      </header>

      {/* Main */}
      <main className="container">

        <section className="hero">
          <h2>Alcohol Label Compliance</h2>

          <p>
            Upload an alcohol beverage label to extract label
            information and screen it against key TTB
            labeling requirements.
          </p>
          <div className="disclaimer">
  <strong>Important:</strong> This tool provides automated
  screening based on selected TTB labeling requirements.
  It is not a substitute for official TTB approval or legal advice.
</div>
        </section>

        {/* Upload */}
        <section className="upload-card">

          <div className={`upload-area ${
    dragActive ? "drag-active" : ""
  }`}
  onDragOver={handleDragOver}
  onDragLeave={handleDragLeave}
  onDrop={handleDrop}>

            {preview ? (
  <>
    <img
      src={preview}
      alt="Alcohol beverage label preview"
      className="label-preview"
    />

    <h3>
      {file?.name}
    </h3>

    <p>
      Image ready for analysis
    </p>
  </>
) : (
  <>
    <div className="upload-icon">
      📄
    </div>

    <h3>
      Drop your label here
    </h3>

    <p>
      or click below to browse
    </p>
  </>
)}

<label className="file-button">
  {preview ? "Choose Different Image" : "Choose Image"}

  <input
    type="file"
    accept="image/png,image/jpeg,image/webp"
    onChange={handleFileChange}
    hidden
  />
</label>

          </div>

          {file && (
            <div className="selected-file">
              Selected: <strong>{file.name}</strong>
            </div>
          )}

          <button
            className="analyze-button"
            onClick={analyzeLabel}
            disabled={!file || analyzing}
          >
            {analyzing
              ? "Analyzing Label..."
              : "Analyze Label"}
          </button>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

        </section>

        {/* Results */}
        {result && (
          <Results result={result} />
        )}

      </main>

      <footer>
        TTB Label Verifier · Prototype
      </footer>

    </div>
  );
}


function Results({ result }) {

  const validation = result.validation;
  const label = result.label;

  const statusClass =
    validation.status.toLowerCase();

  const fields = [
      ["Beverage Type", label.beverage_type],
    ["Brand Name", label.brand_name],
    ["Class / Type", label.class_type],
    ["Alcohol Content", label.alcohol_content],
    ["Proof", label.proof],
    ["Net Contents", label.net_contents],
    ["Producer Name", label.producer_name],
    ["Producer Address", label.producer_address],
      ["Importer Name", label.importer_name],
  ["Importer Address", label.importer_address],
    ["Country of Origin", label.country_of_origin],
    ["Government Warning", label.government_warning],
  ];

  return (
    <section className="results">

      {/* Status */}
     <div className={`result-header ${statusClass}`}>

  <div className="status-main">

    <div className="status-icon">
      {validation.status === "PASS" ? "✓" : "!"}
    </div>

    <div>
      <p className="result-label">
        Compliance Screening Result
      </p>

      <h2>
        {validation.status === "PASS"
          ? "LABEL PASSED"
          : validation.status === "REVIEW"
            ? "LABEL NEEDS REVIEW"
            : "LABEL FAILED"}
      </h2>

      <p className="status-description">
        {validation.status === "PASS"
          ? "All required screening checks passed."
          : `${validation.errors} compliance issue${
              validation.errors === 1 ? "" : "s"
            } detected.`}
      </p>
    </div>

  </div>

  <div className="summary">

    <div>
      <strong>{validation.passed}</strong>
      <span>Passed</span>
    </div>

    <div>
      <strong>{validation.warnings}</strong>
      <span>Warnings</span>
    </div>

    <div>
      <strong>{validation.errors}</strong>
      <span>Errors</span>
    </div>

  </div>

</div>

      {/* Fields */}
      <div className="section">

        <h3>
          Detected Information
        </h3>

        <div className="fields">

          {fields.map(([name, field]) => (

            <div className="field" key={name}>

              <div className="field-name">
                {name}
              </div>

              <div className="field-value">

                {field?.value ? (
                  <>
                    <span className="check">
                      ✓
                    </span>

                    <span>
                      {field.value}
                    </span>
                  </>
                ) : (
                  <>
                    <span className="missing">
                      !
                    </span>

                    <span className="not-detected">
                      Not detected
                    </span>
                  </>
                )}

              </div>

              {field?.confidence != null && (
  <div className="confidence-section">

    <div className="confidence-label">
      <span>AI Confidence</span>

      <strong>
        {Math.round(field.confidence * 100)}%
      </strong>
    </div>

    <div className="confidence-bar">
      <div
        className="confidence-fill"
        style={{
          width: `${field.confidence * 100}%`,
        }}
      />
    </div>

  </div>
)}

{field?.source_text && (
  <div className="source-evidence">

    <div className="source-label">
      Source Evidence
    </div>

    <div className="source-text">
      "{field.source_text}"
    </div>

  </div>
)}

            </div>

          ))}

        </div>

      </div>

      {/* Issues */}
      <div className="section">

        <h3>
          Validation Issues
        </h3>

        {validation.issues.length === 0 ? (

          <div className="no-issues">
            ✓ No validation issues detected
          </div>

        ) : (

          <div className="issues">

            {validation.issues.map(
              (issue, index) => (

                <div
                  className={`issue ${issue.severity}`}
                  key={index}
                >

                  <div className="issue-icon">
                    {issue.severity === "error"
                      ? "✕"
                      : "!"}
                  </div>

                  <div>
                    <strong>
                      {issue.field}
                    </strong>

                    <p>
                      {issue.message}
                    </p>
                  </div>

                </div>

              )
            )}

          </div>

        )}

      </div>

      {/* OCR */}
      <div className="section">

        <details>

          <summary>
            View OCR Text
          </summary>

          <pre className="ocr-text">
            {result.ocr_text}
          </pre>

        </details>

      </div>
    <div className="new-analysis-container">
  <button
    className="new-analysis-button"
    onClick={() => window.location.reload()}
  >
    Analyze Another Label
  </button>
</div>
    </section>
  );
}

export default App;