# Hover documentation for Veeam job option names.
# Keys match XML tag names and bracket-format key names found in Job logs.

OPTION_DOCS = {

    # --- Job identity ---
    'RunManually':                          'Job was started manually. UNRELIABLE — check service or console log instead.',

    # --- Retention ---
    'RetentionType':                        'Retention policy type: 0 = restore points, 1 = days.',
    'RetainCycles':                         'Restore points to keep — the actual job retention setting.',
    'RetainDaysToKeep':                     'Days to keep when using daily retention policy.',
    'CheckRetention':                       'Retention check — seemingly always True.',
    'EnableDeletedVmDataRetention':         '"Remove deleted items after" option enabled.',
    'RetainDays':                           'Days before deleted VMs are removed from backup. NOT job retention (see RetainCycles).',

    # --- Proxy ---
    'SourceProxyAutoDetect':                'Source proxy selection: True = automatic, False = manual.',
    'TargetProxyAutoDetect':                'Target proxy selection (replication only, not applicable to backup).',

    # --- Storage ---
    'StgBlockSize':                         'Storage block size: 256KB / 512KB / 1024KB (default) / 4096KB.',
    'EnableDeduplication':                  'Inline deduplication enabled.',
    'CompressionLevel':                     'Compression: 0 = none, 4 = dedupe-friendly, 5 = optimal (default), 6 = high, 9 = extreme.',
    'StorageEncryptionEnabled':             'Backup file encryption enabled.',
    'ExcludeSwapFile':                      'Exclude swap file blocks.',
    'DirtyBlocksNullingEnabled':            'Exclude deleted file blocks.',

    # --- CBT ---
    'UseChangeTracking':                    'Use changed block tracking (CBT).',
    'EnableChangeTracking':                 'Force-enable CBT on VM if it is disabled.',
    'ResetChangeTrackingOnActiveFull':      'Reset CBT before active full backups.',

    # --- VMware guest ---
    'VMToolsQuiescence':                    'VMware Tools quiescence enabled.',
    'GroupSnapshotProcessing':              'Hyper-V option — not applicable to vSphere backup.',

    # --- Active full / synthetic full ---
    'EnableFullBackup':                     'Active full backup schedule enabled.',
    'FullBackupScheduleKind':               'Active full schedule type: Daily = weekly on selected days, Monthly = monthly.',
    'Algorithm':                            'Backup mode: Increment = incremental (any type), Synthetic = reverse incremental. Does NOT indicate whether the current run is full.',
    'TransformFullToSyntethic':             'Synthetic full schedule enabled.',
    'TransformToSyntethicDays':             'Days when synthetic full backup is scheduled.',
    'TransformIncrementsToSyntethic':       'Transform previous backup chains into rollbacks. No longer effective for new jobs since v11.',

    # --- Health check / compact ---
    'EnableRecheck':                        'Health check enabled.',
    'RecheckScheduleKind':                  'Health check schedule type: Daily = weekly on selected days, Monthly = monthly.',
    'EnableCompactFull':                    '"Defragment and compact full backup file" enabled.',
    'CompactFullBackupScheduleKind':        'Compact full schedule type: Daily = weekly on selected days, Monthly = monthly.',

    # --- VM templates ---
    'Templates':                            '"Backup VM templates" option enabled.',
    'TemplatesOnce':                        '"Exclude templates from incremental backups" enabled.',

    # --- VM notes ---
    'SetResultsToVmNotes':                  'Write successful backup details to a VM attribute.',
    'VmAttributeName':                      'VM attribute name used for backup details.',
    'VmNotesAppend':                        'Append to existing VM attribute value rather than overwrite.',

    # --- SAN / storage integration ---
    'UseSanSnapshots':                      'Storage integration (SAN snapshots) enabled.',
    'MultipleStorageSnapshotEnabled':       'Multiple storage snapshots enabled.',
    'MultipleStorageSnapshotVmsCount':      'Max VMs per storage snapshot when multiple snapshots are enabled.',
    'FailoverFromSan':                      'Failover from SAN to standard backup enabled.',
    'Failover2StorageSnapshotBackup':       'Failover to storage snapshot backup enabled.',

    # --- Scripts ---
    'PostJobCommand':                       'Pre/post job script settings.',
    'PreScriptEnabled':                     'Pre-job script enabled.',
    'Enabled':                              'Post-job script enabled (inside PostJobCommand context).',
    'Periodicity':                          'Script run frequency: Cycles = every N sessions, Days = on selected days.',

    # --- GFS ---
    'GfsPolicy':                            'GFS (Grandfather-Father-Son) retention policy settings.',

    # --- Notifications ---
    'EmailNotification':                    'Job-specific email notifications enabled (independent of global notifications).',
    'UseCustomEmailNotificationOptions':    'Use custom (True) or global (False) notification settings.',
    'EmailNotifyOnSuccess':                 'Send notification on job success.',
    'EmailNotifyOnWarning':                 'Send notification on job warning.',
    'EmailNotifyOnError':                   'Send notification on job error.',
    'EmailNotifyOnLastRetryOnly':           'Send notification only on the last retry attempt.',
    'SnmpNotification':                     'SNMP trap notifications enabled.',

    # --- Guest processing / VSS ---
    'VssSnapshotOptions':                   'Application-aware image processing (AAIP) settings.',
    'ApplicationProcessingEnabled':         'Application processing enabled. Usually True even if AAIP is off.',
    'IgnoreErrors':                         'Try application processing but ignore failures and fall back to crash-consistent.',
    'IsCopyOnly':                           'Perform copy-only backup (no log truncation).',
    'UsePersistentGuestAgent':              'Use persistent guest agents instead of deploying on each run.',

    # --- Indexing ---
    'WinGuestFSIndexingOptions':            'Windows guest file system indexing settings.',
    'LinGuestFSIndexingOptions':            'Linux guest file system indexing settings.',

    # --- SQL ---
    'SqlBackupOptions':                     'SQL Server transaction log processing settings.',
    'TransactionLogsProcessing':            'Log handling: TruncateOnlyOnSuccessJob = truncate, NeverTruncate = do not truncate, Backup = backup periodically.',
    'BackupLogsFrequencyMin':               'SQL transaction log backup interval in minutes.',
    'UseDbBackupRetention':                 'SQL log retention: True = until image-level backup is deleted, False = keep for X days.',
    'ProxyAutoSelect':                      'Log shipping server selection: True = automatic, False = manual.',
    'FailJobOnDbAbsenceOrBackupImpossibility': 'Hidden registry option — fail job if DB is absent or backup is impossible. Always False by default.',

    # --- Exchange ---
    'ExchangeBackupOptions':                'Exchange transaction log processing settings.',

    # --- Credentials ---
    'WinCredsId':                           'Windows guest credentials ID. All zeros = none specified.',
    'LinCredsId':                           'Linux guest credentials ID. All zeros = none specified.',

    # --- Misc ---
    'BackupIsAttached':                     'Purpose unknown.',
}
