import React, { useEffect, useState } from 'react';
import { Store } from '../types/store';
import { ExpectedProduct } from '../types/expected_actual';
import { fetchExpectedProducts, createExpectedProduct, deleteExpectedProduct } from '../services/expected_actual';
import styles from '../pages/Auth.module.css';

interface ExpectedProductManagerProps {
  token: string;
  stores: Store[];
}

export const ExpectedProductManager: React.FC<ExpectedProductManagerProps> = ({ token, stores }) => {
  const [selectedStoreId, setSelectedStoreId] = useState<string>('');
  const [products, setProducts] = useState<ExpectedProduct[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Form inputs
  const [productName, setProductName] = useState<string>('');
  const [productCode, setProductCode] = useState<string>('');
  const [expectedQty, setExpectedQty] = useState<number>(1);
  const [minQty, setMinQty] = useState<number>(1);
  const [maxQty, setMaxQty] = useState<number>(10);
  const [submitting, setSubmitting] = useState<boolean>(false);

  useEffect(() => {
    if (stores.length > 0 && !selectedStoreId) {
      setSelectedStoreId(stores[0].id);
    }
  }, [stores]);

  const loadProducts = async () => {
    if (!token || !selectedStoreId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await fetchExpectedProducts(token, selectedStoreId);
      setProducts(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load expected products.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProducts();
  }, [token, selectedStoreId]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedStoreId) return;

    setSubmitting(true);
    setError(null);
    try {
      await createExpectedProduct(token, {
        store_id: selectedStoreId,
        product_name: productName,
        product_code: productCode,
        expected_quantity: expectedQty,
        expected_min_quantity: minQty,
        expected_max_quantity: maxQty
      });
      setProductName('');
      setProductCode('');
      await loadProducts();
    } catch (err: any) {
      setError(err.message || 'Failed to create expected product.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete expected product expectation?')) return;
    try {
      await deleteExpectedProduct(token, id);
      await loadProducts();
    } catch (err: any) {
      setError(err.message || 'Failed to delete product.');
    }
  };

  return (
    <div className={styles.storesContainer} style={{ marginTop: '2rem' }}>
      <div className={styles.authCard} style={{ maxWidth: '100%', marginBottom: '2rem' }}>
        <h3 className={styles.authTitle} style={{ fontSize: '1.2rem', textAlign: 'left' }}>
          Configure Expected Products Planogram
        </h3>

        {error && <div className={styles.errorMessage}>{error}</div>}

        <form onSubmit={handleCreate} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr auto', gap: '1rem', alignItems: 'end' }}>
          <div className={styles.formGroup} style={{ marginBottom: 0 }}>
            <label className={styles.label}>Select Store</label>
            <select
              className={styles.input}
              value={selectedStoreId}
              onChange={(e) => setSelectedStoreId(e.target.value)}
              required
            >
              {stores.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name} ({s.code})
                </option>
              ))}
            </select>
          </div>

          <div className={styles.formGroup} style={{ marginBottom: 0 }}>
            <label className={styles.label}>Product Name</label>
            <input
              type="text"
              placeholder="e.g. Organic Milk"
              className={styles.input}
              value={productName}
              onChange={(e) => setProductName(e.target.value)}
              required
            />
          </div>

          <div className={styles.formGroup} style={{ marginBottom: 0 }}>
            <label className={styles.label}>Product Code / Class</label>
            <input
              type="text"
              placeholder="e.g. BOTTLE"
              className={styles.input}
              value={productCode}
              onChange={(e) => setProductCode(e.target.value)}
              required
            />
          </div>

          <div className={styles.formGroup} style={{ marginBottom: 0 }}>
            <label className={styles.label}>Qty (Target / Min / Max)</label>
            <div style={{ display: 'flex', gap: '4px' }}>
              <input type="number" min="0" className={styles.input} value={expectedQty} onChange={(e) => setExpectedQty(Number(e.target.value))} style={{ padding: '0.4rem' }} title="Target Quantity" />
              <input type="number" min="0" className={styles.input} value={minQty} onChange={(e) => setMinQty(Number(e.target.value))} style={{ padding: '0.4rem' }} title="Min Quantity" />
              <input type="number" min="0" className={styles.input} value={maxQty} onChange={(e) => setMaxQty(Number(e.target.value))} style={{ padding: '0.4rem' }} title="Max Quantity" />
            </div>
          </div>

          <button type="submit" className={styles.submitBtn} style={{ marginTop: 0 }} disabled={submitting}>
            {submitting ? 'Saving...' : 'Add Product'}
          </button>
        </form>
      </div>

      <h3 style={{ textAlign: 'left', marginBottom: '1rem', color: 'var(--text-primary)' }}>
        Configured Expectations ({products.length})
      </h3>

      {loading ? (
        <p style={{ color: 'var(--text-secondary)' }}>Loading expectations...</p>
      ) : products.length === 0 ? (
        <p style={{ color: 'var(--text-secondary)' }}>No expected products configured for this store location.</p>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          {products.map((p) => (
            <div key={p.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.8rem 1rem', backgroundColor: 'rgba(255,255,255,0.03)', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.08)' }}>
              <div>
                <strong>{p.product_name}</strong> <span style={{ color: '#9ca3af', fontSize: '0.85rem' }}>({p.product_code})</span>
              </div>
              <div style={{ fontSize: '0.9rem' }}>
                Target: <strong>{p.expected_quantity}</strong> | Min: <strong>{p.expected_min_quantity}</strong> | Max: <strong>{p.expected_max_quantity}</strong>
              </div>
              <button
                onClick={() => handleDelete(p.id)}
                style={{ backgroundColor: 'transparent', border: '1px solid #ef4444', color: '#ef4444', padding: '0.2rem 0.6rem', borderRadius: '4px', cursor: 'pointer', fontSize: '0.8rem' }}
              >
                Remove
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
