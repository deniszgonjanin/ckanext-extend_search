import ckan
import pylons
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.model import User, Package, Group
import ckan.model.meta as meta
from ckan.lib.base import c
from sqlalchemy import distinct
from helpers import extend_search_convert_local_to_utc_timestamp

class TemporalPlugin(plugins.SingletonPlugin):
    '''
    Extends the Ckan dataset/package search
    '''

    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IPackageController, inherit=True)


    def update_config(self, config):
        toolkit.add_template_directory(config, 'templates')
        toolkit.add_resource('fanstatic', 'ckanext-temporal')


    # Add the custom parameters to Solr's facet queries
    def before_search(self, search_params):

        extras = search_params.get('extras')
        if not extras:
            # There are no extras in the search params, so do nothing.
            return search_params

        start_date = extend_search_convert_local_to_utc_timestamp(extras.get('ext_startdate'))
        end_date = extend_search_convert_local_to_utc_timestamp(extras.get('ext_enddate'))

        if not start_date or not end_date:
            # The user didn't select any additional params, so do nothing.
            return search_params

        fq = search_params['fq']

        if start_date and end_date:
            # Add a date-range query with the selected start and end dates into the
            # Solr facet queries.
            fq = '{fq} +metadata_modified:[{start_date} TO {end_date}]'.format(
                fq=fq, start_date=start_date, end_date=end_date)

        #return modified facet queries
        search_params['fq'] = fq

        return search_params


    def after_search(self, search_params, search_results):

        return search_params
