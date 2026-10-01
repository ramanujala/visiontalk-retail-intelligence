import React, { useEffect, useState } from 'react';
import { Store } from '../types/store';
import { ComplianceRule } from '../types/compliance';
import { fetchComplianceRules, createComplianceRule, deleteComplianceRule } from '../services/compliance';
import styles from '../pages/Auth.module.css';

interface ComplianceRuleManagerProps {
  token: string;
  stores: Store[];
}

export const ComplianceRuleManager: React.FC<ComplianceRuleManagerProps> = ({ token, stores }) => {
  const [selectedStoreId, setSelectedStoreId] = useState<string>('');
  const [rules, setRules] = useState<ComplianceRule[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [name, setName] = useState<string>('');
  const [description, setDescription] = useState<string>('');
  const [ruleType, setRuleType] = useState<string>('PRODUCT_REQUIRED');
  const [severity, setSeverity] = useState<string>('MEDIUM');
  const [productTarget, setProductTarget] = useState<string>('');
  const [minQty, setMinQty] = useState<number>(1);
  const [submitting, setSubmitting] = useState<boolean>(false);

  const loadRules = async () => {
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      const data = await fetchComplianceRules(token, selectedStoreId || undefined);
      setRules(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load compliance rules.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRules();
  }, [token, selectedStoreId]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    const config: Record<string, any> = {};
    if (ruleType === 'PRODUCT_REQUIRED' || ruleType === 'PRODUCT_QUANTITY') {
      config.product_name = productTarget;
      config.product_code = productTarget;
    }
    if (ruleType === 'PRODUCT_QUANTITY') {
      config.minimum_quantity = minQty;
    }
    if (ruleType === 'OCR_REQUIRED') {
      config.required_text = productTarget;
    }

    try {
      await createComplianceRule(token, {
        name,
        description,
        rule_type: ruleType,
        severity,
        configuration: config,
        store_id: selectedStoreId || undefined,
        is_active: true
      });
      setName('');
      setDescription('');
      setProductTarget('');
      await loadRules();
    } catch (err: any) {
      setError(err.message || 'Failed to create compliance rule.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete compliance rule?')) return;
    try {
      await deleteComplianceRule(token, id);
      await loadRules();
    } catch (err: any) {
      setError(err.message || 'Failed to delete rule.');
    }
  };

  return (
    <div className={styles.storesContainer} style={{ marginTop: '2rem' }}>
      <div className={styles.authCard} style={{ maxWidth: '100%', marginBottom: '2rem' }}>
        <h3 className={styles.authTitle} style={{ fontSize: '1.2rem', textAlign: 'left' }}>
          Configure Retail Compliance Rules
        </h3>

        {error && <div className={styles.errorMessage}>{error}</div>}

        <form onSubmit={handleCreate} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr auto', gap: '1rem', alignItems: 'end' }}>
          <div className={styles.formGroup} style={{ marginBottom: 0 }}>
            <label className={styles.label}>Rule Name</label>
            <input
              type="text"
              placeholder="e.g. Must Have Cola"
              className={styles.input}
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>

          <div className={styles.formGroup} style={{ marginBottom: 0 }}>
            <label className={styles.label}>Rule Type</label>
            <select className={styles.input} value={ruleType} onChange={(e) => setRuleType(e.target.value)}>
              <option value="PRODUCT_REQUIRED">Product Required</option>
              <option value="PRODUCT_QUANTITY">Product Min Quantity</option>
              <option value="UNEXPECTED_PRODUCT">No Unexpected Products</option>
              <option value="OCR_REQUIRED">OCR Text Required</option>
            </select>
          </div>

          <div className={styles.formGroup} style={{ marginBottom: 0 }}>
            <label className={styles.label}>Severity</label>
            <select className={styles.input} value={severity} onChange={(e) => setSeverity(e.target.value)}>
              <option value="LOW">LOW</option>
              <option value="MEDIUM">MEDIUM</option>
              <option value="HIGH">HIGH</option>
              <option value="CRITICAL">CRITICAL</option>
            </select>
          </div>

          <div className={styles.formGroup} style={{ marginBottom: 0 }}>
            <label className={styles.label}>Target Product / Text</label>
            <input
              type="text"
              placeholder="e.g. bottle"
              className={styles.input}
              value={productTarget}
              onChange={(e) => setProductTarget(e.target.value)}
            />
          </div>

          <button type="submit" className={styles.submitBtn} style={{ marginTop: 0 }} disabled={submitting}>
            {submitting ? 'Saving...' : 'Add Rule'}
          </button>
        </form>
      </div>

      <h3 style={{ textAlign: 'left', marginBottom: '1rem', color: 'var(--text-primary)' }}>
        Configured Rules ({rules.length})
      </h3>

      {loading ? (
        <p style={{ color: 'var(--text-secondary)' }}>Loading rules...</p>
      ) : rules.length === 0 ? (
        <p style={{ color: 'var(--text-secondary)' }}>No compliance rules configured.</p>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          {rules.map((r) => (
            <div key={r.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.8rem 1rem', backgroundColor: 'rgba(255,255,255,0.03)', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.08)' }}>
              <div>
                <strong>{r.name}</strong> <span style={{ color: '#9ca3af', fontSize: '0.85rem' }}>[{r.rule_type}]</span>
                {r.description && <div style={{ fontSize: '0.8rem', color: '#9ca3af', marginTop: '2px' }}>{r.description}</div>}
              </div>
              <div style={{ fontSize: '0.85rem' }}>
                SEVERITY: <strong style={{ color: r.severity === 'CRITICAL' || r.severity === 'HIGH' ? '#f87171' : '#fbbf24' }}>{r.severity}</strong>
              </div>
              <button
                onClick={() => handleDelete(r.id)}
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
