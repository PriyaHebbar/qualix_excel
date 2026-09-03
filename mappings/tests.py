from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from connections.models import DataConnection
from mappings.models import Mapping
from accounts.models import UserProfile

class MappingSearchTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        profile, created = UserProfile.objects.get_or_create(user=self.user)
        profile.role = 'contributor'
        profile.save()
        
        self.client.login(username='testuser', password='password123')
        
        self.conn1 = DataConnection.objects.create(
            name='Sales DB',
            connection_type='postgresql',
            host='sales-host',
            database_name='sales_db',
            created_by=self.user
        )
        self.conn2 = DataConnection.objects.create(
            name='Analytics Warehouse',
            connection_type='postgresql',
            host='analytics-host',
            database_name='analytics_db',
            created_by=self.user
        )
        
        self.mapping1 = Mapping.objects.create(
            name='Sales Daily Sync',
            description='Daily pipeline for syncing sales data',
            source_connection=self.conn1,
            source_table='orders',
            target_connection=self.conn2,
            target_table='f_orders',
            created_by=self.user
        )
        
        self.mapping2 = Mapping.objects.create(
            name='Customer Profiles',
            description='Customer CRM extraction pipeline',
            source_connection=self.conn1,
            source_table='customers',
            target_connection=self.conn2,
            target_table='dim_customers',
            created_by=self.user
        )

    def test_list_all_mappings(self):
        response = self.client.get(reverse('mappings:list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['mappings']), 2)

    def test_search_by_name(self):
        response = self.client.get(reverse('mappings:list'), {'query': 'Sync'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['mappings']), 1)
        self.assertEqual(response.context['mappings'][0].name, 'Sales Daily Sync')

    def test_search_by_description(self):
        response = self.client.get(reverse('mappings:list'), {'query': 'CRM'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['mappings']), 1)
        self.assertEqual(response.context['mappings'][0].name, 'Customer Profiles')

    def test_search_by_source_table(self):
        response = self.client.get(reverse('mappings:list'), {'query': 'orders'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['mappings']), 1)
        self.assertEqual(response.context['mappings'][0].name, 'Sales Daily Sync')

    def test_search_by_connection_name(self):
        response = self.client.get(reverse('mappings:list'), {'query': 'Warehouse'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['mappings']), 2)

    def test_search_no_results(self):
        response = self.client.get(reverse('mappings:list'), {'query': 'NonexistentPipeline'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['mappings']), 0)


from mappings.models import Project

class ProjectGroupingTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        profile, created = UserProfile.objects.get_or_create(user=self.user)
        profile.role = 'contributor'
        profile.save()
        self.client.login(username='testuser', password='password123')
        
        self.conn = DataConnection.objects.create(
            name='Test DB',
            connection_type='sqlite',
            host='localhost',
            database_name='test.db',
            created_by=self.user
        )
        
        self.project = Project.objects.create(
            name='Finance Project',
            description='Finance related pipelines',
            created_by=self.user
        )
        
        self.mapping_unassigned = Mapping.objects.create(
            name='Unassigned Sync',
            source_connection=self.conn,
            source_table='table1',
            target_connection=self.conn,
            target_table='table2',
            created_by=self.user
        )
        self.mapping_assigned = Mapping.objects.create(
            name='Finance Sync',
            project=self.project,
            source_connection=self.conn,
            source_table='table3',
            target_connection=self.conn,
            target_table='table4',
            created_by=self.user
        )

    def test_list_all_mappings_ignores_project_filter(self):
        response = self.client.get(reverse('mappings:list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['mappings']), 2)

    def test_list_filter_unassigned(self):
        response = self.client.get(reverse('mappings:list'), {'project': 'unassigned'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['mappings']), 1)
        self.assertEqual(response.context['mappings'][0].id, self.mapping_unassigned.id)

    def test_list_filter_project_id(self):
        response = self.client.get(reverse('mappings:list'), {'project': self.project.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['mappings']), 1)
        self.assertEqual(response.context['mappings'][0].id, self.mapping_assigned.id)

    def test_create_project_api(self):
        url = reverse('mappings:project_create')
        response = self.client.post(url, {
            'name': 'New Project',
            'description': 'A new project description'
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['project']['name'], 'New Project')
        self.assertTrue(Project.objects.filter(name='New Project').exists())
