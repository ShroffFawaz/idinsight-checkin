alert('app.js script has loaded!');

window.onerror = function (message, source, lineno, colno, error) {
    alert(`Global Error: ${message} at ${source}:${lineno}`);
    console.error(error);
};

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM fully loaded and parsed');

    const frontInput = document.getElementById('fileupload');
    const backInput = document.getElementById('bfile');
    const frontInfo = document.getElementById('frontFileInfo');
    const backInfo = document.getElementById('backFileInfo');
    const submitBtn = document.getElementById('submitBtn');

    if (!submitBtn) {
        console.error('Submit button not found!');
        alert('Internal Error: Submit button not found in HTML.');
    } else {
        console.log('Submit button found!');
    }

    function formatBytes(bytes, decimals = 1) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }

    frontInput.addEventListener('change', () => {
        console.log('Front file changed');
        if (frontInput.files.length > 0) {
            const file = frontInput.files[0];
            frontInfo.textContent = `Selected: ${file.name} • ${formatBytes(file.size)}`;
        }
    });

    backInput.addEventListener('change', () => {
        console.log('Back file changed');
        if (backInput.files.length > 0) {
            const file = backInput.files[0];
            backInfo.textContent = `Selected: ${file.name} • ${formatBytes(file.size)}`;
        }
    });

    submitBtn.addEventListener('click', async () => {
        alert('Button clicked! Starting upload logic...');
        console.log('Submit button clicked!');

        const formData = new FormData();
        let hasFiles = false;

        if (frontInput.files.length > 0) {
            formData.append('files', frontInput.files[0]);
            hasFiles = true;
        }

        if (backInput.files.length > 0) {
            formData.append('files', backInput.files[0]);
            hasFiles = true;
        }

        if (!hasFiles) {
            alert('Please select at least one file to upload.');
            return;
        }

        console.log('Starting upload...');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Processing...';

        try {
            console.log('Fetching /file/upload...');
            const response = await fetch('https://idinsight-backend.onrender.com/file/upload', {
                method: 'POST',
                body: formData
            });

            console.log('HTTP Response Status:', response.status);

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Server HTTP Error (${response.status}): ${errorText || response.statusText}`);
            }

            const data = await response.json();
            console.log('Received JSON data:', data);

            if (data.status === 'error') {
                throw new Error(`Server Logic Error: ${data.message}`);
            }

            const fileList = (data.filenames && Array.isArray(data.filenames)) ? data.filenames.join(', ') : 'unknown files';
            const recordId = data.record_id ? ` (Check-in ID: ${data.record_id})` : '';

            alert(`Upload successful!\nProcessed: ${fileList}${recordId}`);
        } catch (error) {
            console.error('Final Catch - Upload failed:', error);
            alert(`Upload failed: ${error.message}`);
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Get Check-in ID';
        }
    });
});
