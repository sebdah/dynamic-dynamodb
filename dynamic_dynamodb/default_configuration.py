""" Default configuration options """
# Default configuration
CONFIGURATION = {
    # Command line only
    'config': None,
    'dry_run': False,

    # [global]
    'aws_region': 'us-east-1',
    'aws_access_key_id': None,
    'aws_secret_access_key': None,
    'check_interval': 300,

    # [logging]
    'log_file': None,
    'log_level': 'info',

    # [table: x]
    'table_name': None,
    'reads_lower_threshold': 30,
    'reads_upper_threshold': 90,
    'increase_reads_with': 50,
    'decrease_reads_with': 50,
    'writes_lower_threshold': 30,
    'writes_upper_threshold': 90,
    'increase_writes_with': 50,
    'decrease_writes_with': 50,
    'min_provisioned_reads': None,
    'max_provisioned_reads': None,
    'min_provisioned_writes': 'apa',
    'max_provisioned_writes': None,
    'allow_scaling_down_reads_on_0_percent': False,
    'allow_scaling_down_writes_on_0_percent': False,
    'always_decrease_rw_together': False,
    'maintenance_windows': None,
}
