import React, { useEffect, useState } from 'react';
import { Store } from '../types/store';
import { ImageItem } from '../types/image';
import { uploadImage, fetchImages, deleteImage } from '../services/images';
import styles from './Auth.module.css';

interface ImageUploadProps {
  token: string;
  stores: Store[];
  onSelectImageForAnalysis?: (image: ImageItem) => void;
}

export const ImageUpload: React.FC<ImageUploadProps> = ({ token, stores, onSelectImageForAnalysis }) => {
  const [selectedStoreId, setSelectedStoreId] = useState<string>('');
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Images state
  const [images, setImages] = useState<ImageItem[]>([]);
  const [loadingImages, setLoadingImages] = useState<boolean>(false);

  // Auto select first store
  useEffect(() => {
    if (stores.length > 0 && !selectedStoreId) {
      setSelectedStoreId(stores[0].id);
    }
  }, [stores]);

  const loadImages = async () => {
    if (!token) return;
    setLoadingImages(true);
    try {
      const res = await fetchImages(token, selectedStoreId || undefined);
      setImages(res.items);
    } catch (err: any) {
      setError(err.message || 'Failed to load images.');
    } finally {
      setLoadingImages(false);
    }
  };

  useEffect(() => {
    loadImages();
  }, [token, selectedStoreId]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
      setSuccessMsg(null);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedStoreId) {
      setError('Please select a store target for upload.');
      return;
    }
    if (!file) {
      setError('Please select an image file to upload.');
      return;
    }

    setUploading(true);
    setError(null);
    setSuccessMsg(null);

    try {
      const uploaded = await uploadImage(token, selectedStoreId, file);
      setSuccessMsg(`Image uploaded successfully! Quality Score: ${uploaded.quality_score}/100`);
      setFile(null);
      await loadImages();
    } catch (err: any) {
      setError(err.message || 'Image upload failed.');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (imageId: string) => {
    if (!confirm('Are you sure you want to delete this image?')) return;
    try {
      await deleteImage(token, imageId);
      await loadImages();
    } catch (err: any) {
      setError(err.message || 'Failed to delete image.');
    }
  };

  return (
    <div className={styles.storesContainer} style={{ marginTop: '2rem' }}>
      <div className={styles.authCard} style={{ maxWidth: '100%', marginBottom: '2rem' }}>
        <h3 className={styles.authTitle} style={{ fontSize: '1.2rem', textAlign: 'left' }}>
          Upload Retail Shelf Image
        </h3>

        {error && <div className={styles.errorMessage}>{error}</div>}
        {successMsg && <div className={styles.successMessage} style={{ backgroundColor: 'rgba(34, 197, 94, 0.1)', color: '#4ade80', padding: '0.8rem', borderRadius: '6px', marginBottom: '1rem' }}>{successMsg}</div>}

        <form onSubmit={handleUpload} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr auto', gap: '1rem', alignItems: 'end' }}>
          <div className={styles.formGroup} style={{ marginBottom: 0 }}>
            <label className={styles.label}>Select Target Store</label>
            <select
              className={styles.input}
              value={selectedStoreId}
              onChange={(e) => setSelectedStoreId(e.target.value)}
              required
            >
              <option value="" disabled>-- Select Store Location --</option>
              {stores.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name} ({s.code})
                </option>
              ))}
            </select>
          </div>

          <div className={styles.formGroup} style={{ marginBottom: 0 }}>
            <label className={styles.label}>Choose Image (JPEG, PNG, WEBP)</label>
            <input
              type="file"
              accept="image/jpeg,image/png,image/webp"
              className={styles.input}
              onChange={handleFileChange}
              required
            />
          </div>

          <button type="submit" className={styles.submitBtn} style={{ marginTop: 0 }} disabled={uploading || !file}>
            {uploading ? 'Uploading...' : 'Upload Image'}
          </button>
        </form>

        {file && (
          <div style={{ marginTop: '0.8rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            Selected: <strong>{file.name}</strong> ({(file.size / (1024 * 1024)).toFixed(2)} MB)
          </div>
        )}
      </div>

      <h3 style={{ textAlign: 'left', marginBottom: '1rem', color: 'var(--text-primary)' }}>
        Uploaded Retail Images ({images.length})
      </h3>

      {loadingImages ? (
        <p style={{ color: 'var(--text-secondary)' }}>Loading images...</p>
      ) : images.length === 0 ? (
        <p style={{ color: 'var(--text-secondary)' }}>No images found for selected store. Upload your first shelf image above.</p>
      ) : (
        <div className={styles.storeGrid}>
          {images.map((img) => (
            <div key={img.id} className={styles.storeCard} style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                <div className={styles.storeName}>{img.original_filename}</div>
                <div className={styles.storeCode}>DIMENSIONS: {img.width} x {img.height} px</div>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.4rem' }}>
                  Size: {(img.file_size / 1024).toFixed(1)} KB | Format: {img.mime_type.split('/')[1].toUpperCase()}
                </div>
                <div style={{ marginTop: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <span style={{
                    padding: '0.2rem 0.6rem',
                    borderRadius: '4px',
                    fontSize: '0.8rem',
                    fontWeight: 600,
                    backgroundColor: img.quality_score >= 70 ? 'rgba(34, 197, 94, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                    color: img.quality_score >= 70 ? '#4ade80' : '#f87171'
                  }}>
                    Quality: {img.quality_score}/100
                  </span>
                  {img.quality_flags.length > 0 && (
                    <span style={{ fontSize: '0.75rem', color: '#f87171' }}>
                      ({img.quality_flags.join(', ')})
                    </span>
                  )}
                </div>
              </div>

              <div style={{ marginTop: '1rem', paddingTop: '0.6rem', borderTop: '1px solid rgba(255,255,255,0.1)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                {onSelectImageForAnalysis ? (
                  <button
                    onClick={() => onSelectImageForAnalysis(img)}
                    style={{
                      backgroundColor: 'var(--primary-color, #3b82f6)',
                      border: 'none',
                      color: '#ffffff',
                      padding: '0.3rem 0.8rem',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontSize: '0.8rem',
                      fontWeight: 600
                    }}
                  >
                    Analyze Objects
                  </button>
                ) : (
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                    {new Date(img.created_at).toLocaleDateString()}
                  </span>
                )}

                <button
                  onClick={() => handleDelete(img.id)}
                  style={{
                    backgroundColor: 'transparent',
                    border: '1px solid #ef4444',
                    color: '#ef4444',
                    padding: '0.2rem 0.6rem',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontSize: '0.8rem'
                  }}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
