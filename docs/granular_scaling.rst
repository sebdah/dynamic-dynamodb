Granular Scaling
================

The granular scaling feature in Dynamic DynamoDB allows users to specify fine tuning for up-scaling read and write
provisioning by using the new optional ``...-scale`` config options.

This new config is specified by providing a dictionary of key-value pairs. The keys are the scaling thresholds for
whichever metric is being evaluated (in percent) and the values are scaling amounts in either ``units`` or ``percent``
depending on the config specified for the associated ``...-unit`` config option.

If the ``...-scale`` config option is not specified then the scaling amount will come from the associated
``...-with`` config option (NOTE: This only applies to the ``increase-consumed-reads-...`` options. For the
``increase-throttled-by-...`` options, if the scale isn't specified then scaling based on these metrics will not occur).

If this option is specified then it will work as follows:

* If the metric being evaluated is at 0% then the scaling amount will be 0
* If the metric being evaluated is at a percentage in the range of scaling thresholds specified the scaling amount
  will be the value of the key-value pair whose key is equal to or lower than the current amount
* If the metric being evaluated is at a higher percentage than the highest threshold specified the scaling amount will
  be the the value of the final key-value pair

Example
-------

Config:
::

    increase-consumed-reads-unit: percent
    increase-consumed-reads-scale: {0: 0, 0.25: 5, 0.5: 10, 1: 20, 2: 50, 5: 100}

In this scenario:

* If the current consumed read units is up to 0.25% no scaling will occur.
* If the current consumed read units is at 0.25% or above but below 0.5% then read provisioning will be scaled up by 5%
* If the current consumed read units is at 0.5% or above but below 1% then read provisioning will be scaled up by 10%
* If the current consumed read units is at 1% or above but below 2% then read provisioning will be scaled up by 20%
* If the current consumed read units is at 2% or above but below 5% then read provisioning will be scaled up by 50%
* If the current consumed read units is at 5% or above read provisioning will be increased by 100%
