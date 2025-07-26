import { useState } from 'react';
import { Download, FileText, Database, AlertTriangle, CheckCircle } from 'lucide-react';
import ApiService from '../../../services/api';
import './DataExport.css';

const DataExport = () => {
  const [isExporting, setIsExporting] = useState(false);
  const [exportStatus, setExportStatus] = useState(null);
  const [selectedFormat, setSelectedFormat] = useState('json');
  const [selectedData, setSelectedData] = useState('all');

  const exportOptions = [
    {
      id: 'all',
      title: 'Complete Export',
      description: 'All your data including tasks, wellness entries, and document metadata',
      icon: <Database size={24} />
    },
    {
      id: 'tasks',
      title: 'Tasks Only',
      description: 'Export only your tasks and productivity data',
      icon: <FileText size={24} />
    },
    {
      id: 'wellness',
      title: 'Wellness Data',
      description: 'Export mood entries and wellness tracking data',
      icon: <CheckCircle size={24} />
    }
  ];

  const formatOptions = [
    {
      id: 'json',
      title: 'JSON Format',
      description: 'Machine-readable format, best for reimporting data',
      extension: '.json'
    },
    {
      id: 'csv',
      title: 'CSV Format',
      description: 'Spreadsheet format, easy to view and analyze',
      extension: '.csv/.zip'
    }
  ];

  const handleExport = async () => {
    setIsExporting(true);
    setExportStatus(null);

    try {
      let endpoint = '/export/data';
      if (selectedData === 'tasks') {
        endpoint = '/export/tasks';
      } else if (selectedData === 'wellness') {
        endpoint = '/export/wellness';
      }

      const response = await fetch(`${ApiService.baseURL}${endpoint}?format=${selectedFormat}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${ApiService.getToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error('Export failed');
      }

      // Get filename from Content-Disposition header
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = `lifesync_export_${new Date().toISOString().split('T')[0]}`;
      
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
        if (filenameMatch) {
          filename = filenameMatch[1];
        }
      }

      // Create blob and download
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      setExportStatus({
        type: 'success',
        message: 'Export completed successfully! Your file has been downloaded.'
      });

    } catch (error) {
      console.error('Export failed:', error);
      setExportStatus({
        type: 'error',
        message: 'Export failed. Please try again or contact support if the problem persists.'
      });
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="data-export">
      <div className="export-header">
        <h2>Export Your Data</h2>
        <p>Download your LifeSync data for backup or to use with other applications.</p>
      </div>

      {/* Data Selection */}
      <div className="export-section">
        <h3>What to Export</h3>
        <div className="export-options">
          {exportOptions.map(option => (
            <div
              key={option.id}
              className={`export-option ${selectedData === option.id ? 'selected' : ''}`}
              onClick={() => setSelectedData(option.id)}
            >
              <div className="option-icon">
                {option.icon}
              </div>
              <div className="option-content">
                <h4>{option.title}</h4>
                <p>{option.description}</p>
              </div>
              <div className="option-radio">
                <input
                  type="radio"
                  name="dataType"
                  value={option.id}
                  checked={selectedData === option.id}
                  onChange={() => setSelectedData(option.id)}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Format Selection */}
      <div className="export-section">
        <h3>Export Format</h3>
        <div className="format-options">
          {formatOptions.map(format => (
            <div
              key={format.id}
              className={`format-option ${selectedFormat === format.id ? 'selected' : ''}`}
              onClick={() => setSelectedFormat(format.id)}
            >
              <input
                type="radio"
                name="format"
                value={format.id}
                checked={selectedFormat === format.id}
                onChange={() => setSelectedFormat(format.id)}
              />
              <div className="format-content">
                <h4>{format.title}</h4>
                <p>{format.description}</p>
                <span className="format-extension">{format.extension}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Export Status */}
      {exportStatus && (
        <div className={`export-status ${exportStatus.type}`}>
          <div className="status-icon">
            {exportStatus.type === 'success' ? (
              <CheckCircle size={20} />
            ) : (
              <AlertTriangle size={20} />
            )}
          </div>
          <span>{exportStatus.message}</span>
        </div>
      )}

      {/* Export Button */}
      <div className="export-action">
        <button
          className="export-button"
          onClick={handleExport}
          disabled={isExporting}
        >
          <Download size={20} />
          {isExporting ? 'Exporting...' : 'Export Data'}
        </button>
      </div>

      {/* Privacy Notice */}
      <div className="privacy-notice">
        <div className="notice-icon">
          <AlertTriangle size={20} />
        </div>
        <div className="notice-content">
          <h4>Privacy & Security</h4>
          <ul>
            <li>Your exported data contains sensitive personal information</li>
            <li>Store exported files securely and delete them when no longer needed</li>
            <li>Document files are not included in exports for security reasons</li>
            <li>Exports are generated in real-time and not stored on our servers</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default DataExport;