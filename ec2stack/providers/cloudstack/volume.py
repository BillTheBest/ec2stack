#!/usr/bin/env python
# encoding: utf-8

import uuid

from ec2stack import errors
from ec2stack import helpers
from ec2stack.providers.cloudstack import requester, disk_offerings, zones


volume_error_to_aws = {
    'unable to find a snapshot': errors.invalid_snapshot_id,
    'Invalid parameter id': errors.invalid_volume_id
}


@helpers.authentication_required
def describe_volumes():
    response = _describe_volumes_request()
    return _describe_volumes_response(response)


def _describe_volumes_request():
    args = {}

    args['command'] = 'listVolumes'

    response = requester.make_request(args)
    response = response['listvolumesresponse']

    return response


def _describe_volumes_response(response):
    return {
        'template_name_or_list': 'volumes.xml',
        'response_type': 'DescribeVolumesResponse',
        'response': response,
    }


@helpers.authentication_required
def create_volume():
    helpers.require_atleast_one_parameter(['SnapshotId', 'Size'])
    response = _create_volume_request()
    return _create_volume_response(response)


def _create_volume_request():
    args = {}

    if helpers.contains_parameter('SnapshotId'):
        args['snapshotid'] = helpers.get('SnapshotId')

    else:
        args['size'] = helpers.get('Size')
        args['diskofferingid'] = \
            disk_offerings.get_disk_offerings_id_by_name('Custom')

    zone_name = helpers.get('AvailabilityZone')
    zone_id = zones.get_zones_id_by_name(zone_name)

    args['zoneid'] = zone_id
    args['command'] = 'createVolume'
    args['name'] = uuid.uuid4()

    response = requester.make_request_async(args)

    return response


def _create_volume_response(response):
    if 'errortext' in response:
        helpers.error_to_aws(response, volume_error_to_aws)

    response = response['volume']
    return {
        'template_name_or_list': 'create_volume.xml',
        'response_type': 'CreateVolumeResponse',
        'response': response
    }


@helpers.authentication_required
def delete_volume():
    helpers.require_parameters(['VolumeId'])
    response = _delete_volume_request()

    return _delete_volume_response(response)


def _delete_volume_request():
    args = {}
    args['id'] = helpers.get('VolumeId')
    args['command'] = 'deleteVolume'

    response = requester.make_request(args)
    response = response['deletevolumeresponse']

    return response


def _delete_volume_response(response):
    if 'errortext' in response:
        helpers.error_to_aws(response, volume_error_to_aws)

    return {
        'template_name_or_list': 'status.xml',
        'response_type': 'DeleteVolumeResponse',
        'return': 'true'
    }
