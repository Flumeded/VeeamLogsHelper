import sublime
import sublime_plugin
import re
import os
import threading

# ---------------------------------------------------------------------------
# Hover documentation for job option names.
# Keys match XML tag names and bracket-format key names found in Job logs.
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# Cache
# Keyed by folder path. Filled once when a Job log is opened; evicted when
# no more log files from that folder are open.
# ---------------------------------------------------------------------------
_cache = {}          # { folder: { 'loaded': bool, 'agent_starts': [], 'agent_sessions': [] } }
_cache_lock = threading.Lock()


def plugin_loaded():
    pass


def plugin_unloaded():
    with _cache_lock:
        _cache.clear()


def _is_job_log(filename):
    return bool(re.match(r'Job\..+\.log$', os.path.basename(filename), re.IGNORECASE))


def _fill_cache(folder):
    """Scan job log files in *folder* and populate the cache entry.
    Runs on a background thread."""
    # Placeholder — agent lookup will be implemented in a later iteration.
    with _cache_lock:
        _cache[folder] = {
            'loaded':         True,
            'agent_starts':   [],
            'agent_sessions': [],
        }


def _evict_if_unused(folder):
    """Remove the cache entry for *folder* if no open views reference it."""
    open_folders = {
        os.path.dirname(v.file_name())
        for w in sublime.windows()
        for v in w.views()
        if v.file_name()
    }
    if folder not in open_folders:
        with _cache_lock:
            _cache.pop(folder, None)


# ---------------------------------------------------------------------------
# Event listener
# ---------------------------------------------------------------------------
class VeeamEventListener(sublime_plugin.EventListener):

    # -- Cache lifecycle -----------------------------------------------------

    def on_load_async(self, view):
        filename = view.file_name()
        if not filename or not _is_job_log(filename):
            return
        folder = os.path.dirname(filename)
        with _cache_lock:
            already = folder in _cache
        if not already:
            with _cache_lock:
                _cache[folder] = {'loaded': False, 'agent_starts': [], 'agent_sessions': []}
            threading.Thread(target=_fill_cache, args=(folder,), daemon=True).start()

    def on_close(self, view):
        filename = view.file_name()
        if not filename:
            return
        # Defer eviction slightly so the view is fully removed first.
        sublime.set_timeout(lambda: _evict_if_unused(os.path.dirname(filename)), 500)

    # -- Hover ---------------------------------------------------------------

    def on_hover(self, view, point, hover_zone):
        if hover_zone != sublime.HOVER_TEXT:
            return
        filename = view.file_name()
        if not filename or not filename.lower().endswith('.log'):
            return

        # 1. Option name lookup (works in both XML and bracket-format lines)
        word = view.substr(view.word(point))
        if word in OPTION_DOCS:
            self._show_option_popup(view, point, word)
            return

        # 2. Agent digest lookup — placeholder for future implementation.

    def _show_option_popup(self, view, point, option_name):
        doc = OPTION_DOCS[option_name]
        body = (
            '<body id="veeam-option-doc">'
            '<style>'
            '  body {{ font-family: sans-serif; font-size: 0.9em; margin: 6px; }}'
            '  .name {{ font-weight: bold; color: var(--yellowish); }}'
            '  .doc  {{ margin-top: 4px; }}'
            '</style>'
            '<div class="name">{0}</div>'
            '<div class="doc">{1}</div>'
            '</body>'
        ).format(option_name, doc)
        view.show_popup(
            body,
            location=point,
            flags=sublime.HIDE_ON_MOUSE_MOVE_AWAY,
            max_width=600,
        )


# ---------------------------------------------------------------------------
# Command: format Job Options XML into a new scratch view
# ---------------------------------------------------------------------------
class VeeamFormatXmlCommand(sublime_plugin.TextCommand):
    """Extract and pretty-print the Job Options XML from the current line.

    Bind to a key in your keymap:
        { "keys": ["ctrl+shift+x"], "command": "veeam_format_xml" }
    """

    def run(self, edit):
        view  = self.view
        point = view.sel()[0].begin()
        line  = view.substr(view.line(point))

        match = re.search(r'(<JobOptionsRoot>.+?</JobOptionsRoot>)', line)
        if not match:
            sublime.status_message('Veeam: no Job Options XML found on this line.')
            return

        import xml.dom.minidom
        try:
            pretty = xml.dom.minidom.parseString(match.group(1)).toprettyxml(indent='    ')
            # Drop the <?xml ...?> declaration line.
            pretty = '\n'.join(pretty.splitlines()[1:])
        except Exception as e:
            sublime.status_message('Veeam: XML parse error — {0}'.format(e))
            return

        new_view = view.window().new_file()
        new_view.set_name('Job Options XML')
        new_view.set_scratch(True)
        new_view.assign_syntax('Packages/XML/XML.sublime-syntax')
        new_view.run_command('append', {'characters': pretty})
