import React, { useState } from 'react';
import { Wifi, WifiOff, RefreshCw, Database, Trash2, Clock, CheckCircle, AlertCircle } from 'lucide-react';
import { useOffline } from '../../contexts/OfflineContext';
import './OfflineIndicator.css';

const OfflineIndicator = () => {
  const { 
    isOnline, 
    syncStatus, 
    cacheSize, 
    manualSync, 
    clearOfflineData, 
    updateCacheSize 
  } = useOffline();
  
  const [showDetails, setShowDetails] = useState(false);
  const [syncLoading, setSyncLoading] = useState(false);
  const [clearLoading, setClearLoading] = useState(false);

  const handleManualSync = async () => {
    if (!isOnline) return;
    
    setSyncLoading(true);
    try {
      await manualSync();
    } catch (error) {
      console.error('Manual sync failed:', error);
    } finally {
      setSyncLoading(false);
    }
  };

  const handleClearCache = async () => {
    if (window.confirm('Are you sure you want to clear all offline data? This cannot be undone.')) {
      setClearLoading(true);
      try {
        await clearOfflineData();
      } catch (error) {
        console.error('Failed to clear cache:', error);
        alert('Failed to clear offline data');
      } finally {
        setClearLoading(false);
      }
    }
  };

  const formatLastSync = (timestamp) => {
    if (!timestamp) return 'Never';
    
    const date = new Date(parseInt(timestamp));
    const now = new Date();
    const diffMinutes = Math.floor((now - date) / (1000 * 60));
    
    if (diffMinutes < 1) return 'Just now';
    if (diffMinutes < 60) return `${diffMinutes}m ago`;
    if (diffMinutes < 1440) return `${Math.floor(diffMinutes / 60)}h ago`;
    return date.toLocaleDateString();
  };

  const getStatusColor = () => {
    if (!isOnline) return 'offline';
    if (syncStatus.inProgress) return 'syncing';
    if (syncStatus.queueSize > 0) return 'pending';
    return 'online';
  };

  const getStatusText = () => {
    if (!isOnline) return 'Offline';
    if (syncStatus.inProgress) return 'Syncing...';
    if (syncStatus.queueSize > 0) return `${syncStatus.queueSize} pending`;
    return 'Online';
  };

  const getStatusIcon = () => {
    if (!isOnline) return <WifiOff size={16} />;
    if (syncStatus.inProgress) return <RefreshCw size={16} className="spinning" />;
    if (syncStatus.queueSize > 0) return <Clock size={16} />;
    return <Wifi size={16} />;
  };

  return (
    <div className="offline-indicator">
      <button 
        className={`status-button ${getStatusColor()}`}
        onClick={() => setShowDetails(!showDetails)}
        title={`Network status: ${getStatusText()}`}
      >
        {getStatusIcon()}
        <span className="status-text">{getStatusText()}</span>
      </button>

      {showDetails && (
        <div className="status-details">
          <div className="details-header">
            <h3>Sync Status</h3>
            <button 
              className="close-btn"
              onClick={() => setShowDetails(false)}
            >
              ×
            </button>
          </div>

          <div className="status-info">
            <div className="info-row">
              <div className="info-label">
                {isOnline ? <Wifi size={14} /> : <WifiOff size={14} />}
                Connection
              </div>
              <div className={`info-value ${isOnline ? 'online' : 'offline'}`}>
                {isOnline ? 'Online' : 'Offline'}
              </div>
            </div>

            <div className="info-row">
              <div className="info-label">
                <Clock size={14} />
                Last Sync
              </div>
              <div className="info-value">
                {formatLastSync(syncStatus.lastSync)}
              </div>
            </div>

            <div className="info-row">
              <div className="info-label">
                <RefreshCw size={14} />
                Sync Queue
              </div>
              <div className="info-value">
                {syncStatus.queueSize} items
                {syncStatus.inProgress && (
                  <span className="sync-indicator">
                    <RefreshCw size={12} className="spinning" />
                  </span>
                )}
              </div>
            </div>

            <div className="info-row">
              <div className="info-label">
                <Database size={14} />
                Cache Size
              </div>
              <div className="info-value">
                {cacheSize.total} items
              </div>
            </div>
          </div>

          <div className="cache-breakdown">
            <h4>Cached Data</h4>
            <div className="cache-items">
              <div className="cache-item">
                <span>Tasks</span>
                <span>{cacheSize.tasks || 0}</span>
              </div>
              <div className="cache-item">
                <span>Sync Queue</span>
                <span>{cacheSize.syncQueue || 0}</span>
              </div>
              <div className="cache-item">
                <span>User Data</span>
                <span>{cacheSize.userData || 0}</span>
              </div>
            </div>
          </div>

          <div className="status-actions">
            <button 
              className="sync-btn"
              onClick={handleManualSync}
              disabled={!isOnline || syncLoading || syncStatus.inProgress}
            >
              <RefreshCw size={14} className={syncLoading ? 'spinning' : ''} />
              {syncLoading ? 'Syncing...' : 'Sync Now'}
            </button>

            <button 
              className="clear-btn"
              onClick={handleClearCache}
              disabled={clearLoading}
            >
              <Trash2 size={14} />
              {clearLoading ? 'Clearing...' : 'Clear Cache'}
            </button>
          </div>

          {syncStatus.queueSize > 0 && (
            <div className="sync-warning">
              <AlertCircle size={14} />
              <span>
                You have {syncStatus.queueSize} changes waiting to sync. 
                {!isOnline && ' Connect to the internet to sync your changes.'}
              </span>
            </div>
          )}

          {!isOnline && (
            <div className="offline-notice">
              <WifiOff size={14} />
              <span>
                You're working offline. Your changes will sync automatically when you're back online.
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default OfflineIndicator;