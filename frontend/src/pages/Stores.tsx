import React, { useEffect, useState } from 'react';
import { Store } from '../types/store';
import { fetchStores, createStore } from '../services/stores';
import styles from './Auth.module.css';

interface StoresProps {
  token: string;
}

export const Stores: React.FC<StoresProps> = ({ token }) => {
  const [stores, setStores] = useState<Store[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Form State
  const [name, setName] = useState('');
  const [code, setCode] = useState('');
  const [location, setLocation] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const loadStores = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchStores(token);
      setStores(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load stores.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStores();
  }, [token]);

  const handleCreateStore = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await createStore(token, { name, code, location });
      setName('');
      setCode('');
      setLocation('');
      await loadStores();
    } catch (err: any) {
      setError(err.message || 'Failed to create store.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className={styles.storesContainer}>
      <div className={styles.authCard} style={{ maxWidth: '100%', marginBottom: '2rem' }}>
        <h3 className={styles.authTitle} style={{ fontSize: '1.2rem', textAlign: 'left' }}>
          Add New Store Location
        </h3>
        {error && <div className={styles.errorMessage}>{error}</div>}
        <form onSubmit={handleCreateStore} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr auto', gap: '1rem', alignItems: 'end' }}>
          <div className={styles.formGroup} style={{ marginBottom: 0 }}>
            <label className={styles.label}>Store Name</label>
            <input
              type="text"
              className={styles.input}
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Downtown Market"
              required
            />
          </div>
          <div className={styles.formGroup} style={{ marginBottom: 0 }}>
            <label className={styles.label}>Store Code</label>
            <input
              type="text"
              className={styles.input}
              value={code}
              onChange={(e) => setCode(e.target.value.toUpperCase())}
              placeholder="STR-001"
              required
            />
          </div>
          <div className={styles.formGroup} style={{ marginBottom: 0 }}>
            <label className={styles.label}>Location</label>
            <input
              type="text"
              className={styles.input}
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="123 Main St"
            />
          </div>
          <button type="submit" className={styles.submitBtn} style={{ marginTop: 0 }} disabled={submitting}>
            {submitting ? 'Adding...' : 'Add Store'}
          </button>
        </form>
      </div>

      <h3 style={{ textAlign: 'left', marginBottom: '1rem', color: 'var(--text-primary)' }}>
        Tenant Stores ({stores.length})
      </h3>

      {loading ? (
        <p style={{ color: 'var(--text-secondary)' }}>Loading stores...</p>
      ) : stores.length === 0 ? (
        <p style={{ color: 'var(--text-secondary)' }}>No stores found. Add your first store location above.</p>
      ) : (
        <div className={styles.storeGrid}>
          {stores.map((store) => (
            <div key={store.id} className={styles.storeCard}>
              <div className={styles.storeName}>{store.name}</div>
              <div className={styles.storeCode}>CODE: {store.code}</div>
              {store.location && <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.4rem' }}>{store.location}</div>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
