import { useState, useCallback, useRef } from "react";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

// SVG Icons as components
const Icons = {
  chair: () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M5 11V7a2 2 0 012-2h10a2 2 0 012 2v4M5 11h14M5 11v2a2 2 0 002 2h10a2 2 0 002-2v-2M7 15v4M17 15v4M9 19h6"/>
    </svg>
  ),
  book: () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M4 19.5A2.5 2.5 0 016.5 17H20M4 19.5A2.5 2.5 0 016.5 22H20V4H6.5A2.5 2.5 0 004 6.5v13z"/>
    </svg>
  ),
  tv: () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <rect x="2" y="5" width="20" height="14" rx="2"/>
      <path d="M8 21h8M12 19v2"/>
    </svg>
  ),
  laptop: () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M4 6a2 2 0 012-2h12a2 2 0 012 2v9H4V6zM2 17h20l-2 3H4l-2-3z"/>
    </svg>
  ),
  phone: () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <rect x="5" y="2" width="14" height="20" rx="2"/>
      <path d="M12 18h.01"/>
    </svg>
  ),
  cup: () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M17 8h1a4 4 0 010 8h-1M3 8h14v9a4 4 0 01-4 4H7a4 4 0 01-4-4V8zM6 2v3M10 2v3M14 2v3"/>
    </svg>
  ),
  clock: () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <circle cx="12" cy="12" r="10"/>
      <path d="M12 6v6l4 2"/>
    </svg>
  ),
  frame: () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <rect x="3" y="3" width="18" height="18" rx="2"/>
      <circle cx="8.5" cy="8.5" r="1.5"/>
      <path d="M21 15l-5-5-11 11"/>
    </svg>
  ),
  lamp: () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M9 18h6M10 22h4M12 2v1M12 18v4M5.6 5.6l.7.7M18.4 5.6l-.7.7M4 12H3M21 12h-1M7 12a5 5 0 1110 0c0 2-1.5 3.5-3 4.5V18H10v-1.5c-1.5-1-3-2.5-3-4.5z"/>
    </svg>
  ),
  plant: () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M12 22V10M12 10C12 10 12 4 7 4c0 5 5 6 5 6zM12 10c0 0 0-4 5-4 0 4-5 4-5 4zM12 14c-3 0-5 2-5 4h10c0-2-2-4-5-4z"/>
      <path d="M7 22h10"/>
    </svg>
  ),
  couch: () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M4 12V8a2 2 0 012-2h12a2 2 0 012 2v4M2 12v4a2 2 0 002 2h16a2 2 0 002-2v-4a2 2 0 00-2-2H4a2 2 0 00-2 2zM6 18v2M18 18v2"/>
    </svg>
  ),
  bed: () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M3 13V7a2 2 0 012-2h14a2 2 0 012 2v6M3 13h18M3 13v4M21 13v4M3 17h18M6 10h3v3H6z"/>
    </svg>
  ),
  custom: () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <circle cx="12" cy="12" r="10"/>
      <path d="M12 8v8M8 12h8"/>
    </svg>
  ),
  photo: () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <rect x="3" y="3" width="18" height="18" rx="2"/>
      <circle cx="8.5" cy="8.5" r="1.5"/>
      <path d="M21 15l-5-5L5 21"/>
    </svg>
  ),
  video: () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <rect x="2" y="4" width="15" height="16" rx="2"/>
      <path d="M17 8l5-3v14l-5-3V8z"/>
    </svg>
  ),
  audio: () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M12 3v18M8 8v8M4 10v4M16 8v8M20 10v4"/>
    </svg>
  ),
  file: () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z"/>
      <path d="M14 2v6h6M16 13H8M16 17H8M10 9H8"/>
    </svg>
  ),
  upload: () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12"/>
    </svg>
  ),
  close: () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M18 6L6 18M6 6l12 12"/>
    </svg>
  ),
};

const OBJECT_OPTIONS = [
  { value: "chair", label: "Chair", icon: "chair" },
  { value: "book", label: "Book", icon: "book" },
  { value: "tv", label: "Television", icon: "tv" },
  { value: "laptop", label: "Computer", icon: "laptop" },
  { value: "phone", label: "Phone", icon: "phone" },
  { value: "cup", label: "Cup / Mug", icon: "cup" },
  { value: "clock", label: "Clock", icon: "clock" },
  { value: "picture", label: "Picture", icon: "frame" },
  { value: "lamp", label: "Lamp", icon: "lamp" },
  { value: "plant", label: "Plant", icon: "plant" },
  { value: "couch", label: "Couch", icon: "couch" },
  { value: "bed", label: "Bed", icon: "bed" },
];

/**
 * Memory upload panel - multimodal support for photos, videos, audio, text.
 */
export default function MemoryUpload({ onClose, onSaved }) {
  const [step, setStep] = useState(1);
  const [objectLabel, setObjectLabel] = useState("");
  const [isCustom, setIsCustom] = useState(false);
  const [customLabel, setCustomLabel] = useState("");
  const [title, setTitle] = useState("");
  const [memoryText, setMemoryText] = useState("");
  const [files, setFiles] = useState([]);
  const [saving, setSaving] = useState(false);
  const [status, setStatus] = useState(null);
  
  const fileInputRef = useRef(null);

  const finalLabel = isCustom ? customLabel.toLowerCase().trim() : objectLabel;
  const selectedObject = OBJECT_OPTIONS.find(o => o.value === objectLabel);

  const handleObjectSelect = (value) => {
    setObjectLabel(value);
    setIsCustom(false);
  };

  const handleCustomSelect = () => {
    setObjectLabel("");
    setIsCustom(true);
  };

  const handleFileSelect = useCallback((e) => {
    const newFiles = Array.from(e.target.files).map(file => {
      const type = file.type.startsWith('image/') ? 'image' 
                 : file.type.startsWith('video/') ? 'video'
                 : file.type.startsWith('audio/') ? 'audio'
                 : 'document';
      
      return {
        file,
        type,
        preview: type === 'image' ? URL.createObjectURL(file) : null,
        name: file.name,
      };
    });
    
    setFiles(prev => [...prev, ...newFiles]);
    e.target.value = '';
  }, []);

  const removeFile = useCallback((index) => {
    setFiles(prev => {
      const removed = prev[index];
      if (removed.preview) URL.revokeObjectURL(removed.preview);
      return prev.filter((_, i) => i !== index);
    });
  }, []);

  const handleSave = useCallback(async () => {
    // Require object label
    if (!finalLabel) {
      setStatus({ type: "error", msg: "Please select an object" });
      return;
    }

    // Either files OR manual text is required
    const hasFiles = files.length > 0;
    const hasManualText = memoryText.trim().length > 0;
    
    if (!hasFiles && !hasManualText) {
      setStatus({ type: "error", msg: "Please add files or write a memory" });
      return;
    }

    setSaving(true);

    try {
      let res;

      if (hasFiles) {
        // Upload files and let AI generate memory
        setStatus({ type: "info", msg: "Uploading files and creating memory..." });
        
        const formData = new FormData();
        formData.append("object_label", finalLabel);
        if (title.trim()) {
          formData.append("title", title.trim());
        }
        
        for (const f of files) {
          formData.append("files", f.file);
        }

        res = await fetch(`${API_BASE}/upload/memory`, {
          method: "POST",
          body: formData,
        });
      } else {
        // Manual text entry (legacy flow)
        if (!title.trim()) {
          setStatus({ type: "error", msg: "Please give your memory a title" });
          setSaving(false);
          return;
        }
        
        setStatus({ type: "info", msg: "Saving your memory..." });
        
        res = await fetch(`${API_BASE}/memory`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            object_label: finalLabel,
            title: title.trim(),
            memory_text: memoryText.trim(),
            audio_url: null,
          }),
        });
      }

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || "Could not save");
      }

      setStatus({ type: "success", msg: "Memory saved!" });
      
      setTimeout(() => {
        onSaved?.();
        onClose?.();
      }, 1200);
    } catch (err) {
      setStatus({ type: "error", msg: err.message || "Could not save. Please try again." });
    } finally {
      setSaving(false);
    }
  }, [finalLabel, title, memoryText, files, onSaved, onClose]);

  const IconComponent = ({ name, className }) => {
    const Icon = Icons[name];
    return Icon ? <span className={className}><Icon /></span> : null;
  };

  const canProceed = isCustom ? customLabel.trim().length > 0 : objectLabel.length > 0;

  return (
    <div className="upload-overlay" onClick={onClose}>
      <div className="upload-panel" onClick={e => e.stopPropagation()}>
        
        {/* Header */}
        <div className="upload-panel__header">
          <div className="upload-panel__header-content">
            <h2 className="upload-panel__title">Add a Memory</h2>
            <p className="upload-panel__subtitle">
              {step === 1 ? "What object holds this memory?" : "Tell us about this memory"}
            </p>
          </div>
          <button className="upload-panel__close" onClick={onClose} aria-label="Close">
            <IconComponent name="close" />
          </button>
        </div>

        {/* Step 1: Choose Object */}
        {step === 1 && (
          <div className="upload-panel__step">
            <div className="upload-panel__objects">
              {OBJECT_OPTIONS.map((obj) => (
                <button
                  key={obj.value}
                  className={`upload-panel__object-btn ${objectLabel === obj.value && !isCustom ? 'selected' : ''}`}
                  onClick={() => handleObjectSelect(obj.value)}
                >
                  <IconComponent name={obj.icon} className="upload-panel__object-icon" />
                  <span className="upload-panel__object-label">{obj.label}</span>
                </button>
              ))}
              
              {/* Custom object option */}
              <button
                className={`upload-panel__object-btn ${isCustom ? 'selected' : ''}`}
                onClick={handleCustomSelect}
              >
                <IconComponent name="custom" className="upload-panel__object-icon" />
                <span className="upload-panel__object-label">Other...</span>
              </button>
            </div>

            {/* Custom label input */}
            {isCustom && (
              <div className="upload-panel__custom-field">
                <input
                  type="text"
                  className="upload-panel__input"
                  value={customLabel}
                  onChange={(e) => setCustomLabel(e.target.value)}
                  placeholder="Enter object name (e.g., piano, mirror, rug)"
                  autoFocus
                />
              </div>
            )}

            <button
              className="upload-panel__next-btn"
              onClick={() => setStep(2)}
              disabled={!canProceed}
            >
              Continue
            </button>
          </div>
        )}

        {/* Step 2: Add Content */}
        {step === 2 && (
          <div className="upload-panel__step">
            <div className="upload-panel__selected-object">
              {isCustom ? (
                <IconComponent name="custom" className="upload-panel__selected-icon" />
              ) : (
                <IconComponent name={selectedObject?.icon} className="upload-panel__selected-icon" />
              )}
              <span>
                Memory for: <strong>{isCustom ? customLabel : selectedObject?.label}</strong>
              </span>
              <button className="upload-panel__change-btn" onClick={() => setStep(1)}>
                Change
              </button>
            </div>

            {/* Title */}
            <div className="upload-panel__field">
              <label className="upload-panel__label">Give this memory a name</label>
              <input
                type="text"
                className="upload-panel__input"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g., Sunday dinners with grandma"
              />
            </div>

            {/* File Upload - Primary option */}
            <div className="upload-panel__field">
              <label className="upload-panel__label">
                Add photos, documents, or recordings
                <span className="upload-panel__label-hint"> (AI will create the memory)</span>
              </label>
              
              <div className="upload-panel__dropzone" onClick={() => fileInputRef.current?.click()}>
                <IconComponent name="upload" className="upload-panel__dropzone-icon" />
                <span className="upload-panel__dropzone-text">
                  Tap to add files
                </span>
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  accept="image/*,video/*,audio/*,.pdf,.doc,.docx"
                  onChange={handleFileSelect}
                  style={{ display: 'none' }}
                />
              </div>

              {/* File Previews */}
              {files.length > 0 && (
                <div className="upload-panel__files">
                  {files.map((f, i) => (
                    <div key={i} className="upload-panel__file">
                      {f.type === 'image' && f.preview ? (
                        <img src={f.preview} alt="" className="upload-panel__file-preview" />
                      ) : (
                        <div className="upload-panel__file-icon-wrap">
                          <IconComponent 
                            name={f.type === 'video' ? 'video' : f.type === 'audio' ? 'audio' : 'file'} 
                            className="upload-panel__file-type-icon"
                          />
                        </div>
                      )}
                      <span className="upload-panel__file-name">{f.name}</span>
                      <button 
                        className="upload-panel__file-remove"
                        onClick={() => removeFile(i)}
                        aria-label="Remove"
                      >
                        <IconComponent name="close" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Divider when no files */}
            {files.length === 0 && (
              <div className="upload-panel__divider">
                <span>or write it yourself</span>
              </div>
            )}

            {/* Story - Optional when files are provided */}
            {files.length === 0 && (
              <div className="upload-panel__field">
                <label className="upload-panel__label">Tell the story</label>
                <textarea
                  className="upload-panel__textarea"
                  value={memoryText}
                  onChange={(e) => setMemoryText(e.target.value)}
                  placeholder="Who was there? What happened? What made it special?"
                  rows={4}
                />
              </div>
            )}

            {/* Status */}
            {status && (
              <div className={`upload-panel__status upload-panel__status--${status.type}`}>
                {status.msg}
              </div>
            )}

            {/* Actions */}
            <div className="upload-panel__actions">
              <button className="upload-panel__back-btn" onClick={() => setStep(1)}>
                Back
              </button>
              <button
                className="upload-panel__save-btn"
                onClick={handleSave}
                disabled={saving || (files.length === 0 && (!title.trim() || !memoryText.trim()))}
              >
                {saving ? (files.length > 0 ? "Creating..." : "Saving...") : "Save Memory"}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
