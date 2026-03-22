document.addEventListener("DOMContentLoaded", () => {
    let currentFile = null;

    // UI Elements
    const dropzone = document.getElementById("dropzone");
    const fileLabel = document.getElementById("fileLabel");
    const fileInput = document.getElementById("fileInput");
    const openBtn = document.getElementById("openBtn");
    const hashBtn = document.getElementById("hashBtn");
    const aboutBtn = document.getElementById("aboutBtn");
    const progressFill = document.getElementById("progressFill");
    const statusLabel = document.getElementById("statusLabel");

    // UI Helpers
    function setStatus(msg, colorStr) {
        statusLabel.textContent = msg;
        statusLabel.style.color = colorStr || "var(--fg-dim)";
    }

    function setProgress(percent) {
        progressFill.style.width = `${percent}%`;
    }

    function loadFile(file) {
        if (!file) return;
        currentFile = file;
        fileLabel.textContent = `📄 ${file.name}`;
        hashBtn.disabled = false;
        setStatus("Αρχείο επιλέχθηκε — πατήστε «Δημιουργία PDF»", "var(--fg-dim)");
        setProgress(0);
    }

    // Interactions
    aboutBtn.addEventListener("click", () => {
        alert("DXF Hash → PDF\n\ndnikolos@gmail.com");
    });

    openBtn.addEventListener("click", () => {
        fileInput.click();
    });

    dropzone.addEventListener("click", () => {
        if (event.target !== fileInput) {
            fileInput.click();
        }
    });

    fileInput.addEventListener("change", (e) => {
        if (e.target.files.length > 0) {
            loadFile(e.target.files[0]);
        }
    });

    // Drag-and-drop
    dropzone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropzone.classList.add("drag-hover");
    });

    dropzone.addEventListener("dragleave", (e) => {
        e.preventDefault();
        dropzone.classList.remove("drag-hover");
    });

    dropzone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropzone.classList.remove("drag-hover");
        if (e.dataTransfer.files.length > 0) {
            loadFile(e.dataTransfer.files[0]);
            fileInput.files = e.dataTransfer.files; // Sync the file input as well
        }
    });

    // Core Logic
    hashBtn.addEventListener("click", async () => {
        if (!currentFile) return;

        hashBtn.disabled = true;
        setStatus("Υπολογισμός hash…", "var(--fg-dim)");
        setProgress(5);

        try {
            // STEP 1: Read the file efficiently using FileReader
            const arrayBuffer = await new Promise((resolve, reject) => {
                const reader = new FileReader();
                reader.onprogress = (e) => {
                    if (e.lengthComputable) {
                        const percent = 5 + Math.round((e.loaded / e.total) * 45); // 5% to 50%
                        setProgress(percent);
                    }
                };
                reader.onload = (e) => {
                    setProgress(50);
                    resolve(e.target.result);
                };
                reader.onerror = () => reject(new Error("Σφάλμα ανάγνωσης αρχείου"));
                reader.readAsArrayBuffer(currentFile);
            });

            setProgress(60);

            // STEP 2: Use Native Web Crypto API to calculate SHA-512
            // Extremely fast, runs at native speeds in the browser
            const hashBuffer = await crypto.subtle.digest("SHA-512", arrayBuffer);
            const hashArray = Array.from(new Uint8Array(hashBuffer));
            const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
            
            setProgress(85);
            setStatus("Δημιουργία PDF…", "var(--fg-dim)");

            // STEP 3: Create PDF
            const { jsPDF } = window.jspdf;
            const doc = new jsPDF('p', 'mm', 'a4');
            doc.setFont("helvetica", "normal");
            doc.setFontSize(12);

            // Split the long 128-char hex string to ensure it fits the A4 page width
            const splitText = doc.splitTextToSize(hashHex, 190);
            doc.text(splitText, 10, 15);

            const outFilename = `${currentFile.name}_hash.pdf`;
            doc.save(outFilename); // Forces a local download to user's machine

            // STEP 4: Update UI
            setProgress(100);
            setStatus(`✓ ${outFilename} δημιουργήθηκε`, "var(--success)");

        } catch (err) {
            console.error(err);
            setProgress(0);
            setStatus(`✗ Σφάλμα: ${err.message || "Άγνωστο σφάλμα"}`, "var(--error)");
        } finally {
            hashBtn.disabled = false;
        }
    });
});
