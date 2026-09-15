import React, { useState } from 'react';
import { registerCompany } from '../services/auth';
import styles from './Auth.module.css';

interface RegisterProps {
  onSuccess: (token: string) => void;
  onSwitchToLogin: () => void;
}

export const Register: React.FC<RegisterProps> = ({ onSuccess, onSwitchToLogin }) => {
  const [companyName, setCompanyName] = useState('');
  const [companySlug, setCompanySlug] = useState('');
  const [adminEmail, setAdminEmail] = useState('');
  const [adminPassword, setAdminPassword] = useState('');
  const [adminFullName, setAdminFullName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const data = await registerCompany({
        company_name: companyName,
        company_slug: companySlug,
        admin_email: adminEmail,
        admin_password: adminPassword,
        admin_full_name: adminFullName,
      });
      onSuccess(data.access_token);
    } catch (err: any) {
      setError(err.message || 'Registration failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.authCard}>
      <h2 className={styles.authTitle}>Register Company Workspace</h2>
      <p className={styles.authSubtitle}>Create an administrative tenant workspace</p>

      {error && <div className={styles.errorMessage}>{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className={styles.formGroup}>
          <label className={styles.label}>Company Name</label>
          <input
            type="text"
            className={styles.input}
            value={companyName}
            onChange={(e) => setCompanyName(e.target.value)}
            placeholder="Vision Retail Solutions"
            required
          />
        </div>

        <div className={styles.formGroup}>
          <label className={styles.label}>Company Slug</label>
          <input
            type="text"
            className={styles.input}
            value={companySlug}
            onChange={(e) => setCompanySlug(e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, ''))}
            placeholder="vision-retail"
            required
          />
        </div>

        <div className={styles.formGroup}>
          <label className={styles.label}>Admin Full Name</label>
          <input
            type="text"
            className={styles.input}
            value={adminFullName}
            onChange={(e) => setAdminFullName(e.target.value)}
            placeholder="Sarah Connor"
            required
          />
        </div>

        <div className={styles.formGroup}>
          <label className={styles.label}>Admin Email</label>
          <input
            type="email"
            className={styles.input}
            value={adminEmail}
            onChange={(e) => setAdminEmail(e.target.value)}
            placeholder="admin@visionretail.com"
            required
          />
        </div>

        <div className={styles.formGroup}>
          <label className={styles.label}>Admin Password</label>
          <input
            type="password"
            className={styles.input}
            value={adminPassword}
            onChange={(e) => setAdminPassword(e.target.value)}
            placeholder="Min 8 characters"
            required
            minLength={8}
          />
        </div>

        <button type="submit" className={styles.submitBtn} disabled={loading}>
          {loading ? 'Creating Workspace...' : 'Register Company'}
        </button>
      </form>

      <div className={styles.toggleContainer}>
        Already have a company account?
        <span className={styles.toggleLink} onClick={onSwitchToLogin}>
          Sign In
        </span>
      </div>
    </div>
  );
};
