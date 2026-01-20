# Copyright 2026 Acryl Data, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from unittest.mock import MagicMock, Mock, patch

import pytest
from datahub_actions.pipeline.pipeline_context import PipelineContext

from action_glossary_export.config import GlossaryExportConfig
from action_glossary_export.glossary_export_action import GlossaryExportAction
from action_glossary_export.transformers import (
    build_hierarchical_path,
    transform_entity_to_row,
    transform_usage_to_row,
)


@pytest.fixture
def mock_config():
    """Create a mock configuration for testing"""
    return {
        "connection": {
            "account_id": "test-account",
            "username": "test-user",
            "password": "test-password",
            "warehouse": "TEST_WH",
            "authentication_type": "DEFAULT_AUTHENTICATOR",
        },
        "destination": {
            "database": "TEST_DB",
            "schema": "TEST_SCHEMA",
            "table_name": "test_glossary_export",
        },
        "export_on_startup": False,
        "batch_size": 100,
    }


@pytest.fixture
def mock_pipeline_context():
    """Create a mock pipeline context"""
    ctx = Mock(spec=PipelineContext)
    ctx.graph = MagicMock()
    return ctx


@pytest.fixture
def sample_glossary_term():
    """Sample glossary term data"""
    return {
        "urn": "urn:li:glossaryTerm:test-term",
        "type": "GLOSSARY_TERM",
        "name": "Test Term",
        "hierarchicalName": "Finance > Test Term",
        "properties": {
            "name": "Test Term",
            "description": "A test glossary term",
            "definition": "Test definition",
            "createdOn": {"time": 1700000000000},
            "customProperties": [
                {"key": "classification", "value": "PII"},
                {"key": "criticality", "value": "high"},
            ],
        },
        "parentNodes": {
            "nodes": [
                {
                    "urn": "urn:li:glossaryNode:finance",
                    "properties": {"name": "Finance"},
                }
            ]
        },
        "domain": {
            "domain": {
                "urn": "urn:li:domain:finance-domain",
                "properties": {"name": "Finance Domain"},
            }
        },
        "ownership": {
            "owners": [
                {
                    "owner": {
                        "urn": "urn:li:corpuser:jdoe",
                        "username": "jdoe",
                    },
                    "type": "TECHNICAL_OWNER",
                }
            ]
        },
    }


@pytest.fixture
def sample_glossary_node():
    """Sample glossary node data"""
    return {
        "urn": "urn:li:glossaryNode:finance",
        "type": "GLOSSARY_NODE",
        "properties": {
            "name": "Finance",
            "description": "Finance glossary node",
            "createdOn": {"time": 1700000000000},
        },
        "parentNodes": {"nodes": []},
        "ownership": {"owners": []},
    }


@pytest.fixture
def sample_dashboard_entity():
    """Sample Power BI dashboard entity using a glossary term"""
    return {
        "urn": "urn:li:dashboard:(powerbi,sales-dashboard)",
        "type": "DASHBOARD",
        "properties": {
            "name": "Sales Dashboard",
            "description": "Dashboard showing sales metrics",
        },
        "platform": {"name": "powerbi"},
        "subTypes": {"typeNames": ["Report"]},
        "container": {
            "urn": "urn:li:container:workspace123",
            "properties": {"name": "Sales Workspace"},
        },
        "domain": {
            "domain": {"urn": "urn:li:domain:sales-domain", "properties": {"name": "Sales Domain"}}
        },
    }


@pytest.fixture
def sample_dataset_entity():
    """Sample Snowflake dataset entity using a glossary term"""
    return {
        "urn": "urn:li:dataset:(urn:li:dataPlatform:snowflake,db.schema.customer_revenue,PROD)",
        "type": "DATASET",
        "properties": {
            "name": "customer_revenue",
            "description": "Customer revenue data",
        },
        "platform": {"name": "snowflake"},
        "subTypes": {"typeNames": ["Table"]},
        "container": {"urn": "urn:li:container:db.schema", "properties": {"name": "schema"}},
        "domain": {
            "domain": {"urn": "urn:li:domain:analytics", "properties": {"name": "Analytics"}}
        },
    }


class TestGlossaryExportConfig:
    def test_config_validation(self, mock_config):
        """Test that config validates correctly"""
        config = GlossaryExportConfig.model_validate(mock_config)
        assert config.connection.account_id == "test-account"
        assert config.destination.table_name == "test_glossary_export"
        assert config.export_on_startup is False
        assert config.batch_size == 100

    def test_config_defaults(self):
        """Test default values in config"""
        minimal_config = {
            "connection": {
                "account_id": "test",
                "username": "test",
                "password": "test",
            },
            "destination": {
                "database": "test",
                "schema": "test",
            },
        }
        config = GlossaryExportConfig.model_validate(minimal_config)
        assert config.export_on_startup is True
        assert config.batch_size == 1000
        assert config.destination.table_name == "datahub_glossary_export"
        assert config.entity_types == ["DASHBOARD"]


class TestGlossaryExportAction:
    @patch(
        "datahub.ingestion.source.snowflake.snowflake_connection.SnowflakeConnectionConfig.get_native_connection"
    )
    def test_create_action(self, mock_get_connection, mock_config, mock_pipeline_context):
        """Test action creation"""
        mock_get_connection.return_value = MagicMock()
        action = GlossaryExportAction.create(mock_config, mock_pipeline_context)
        assert isinstance(action, GlossaryExportAction)
        assert action.config.connection.account_id == "test-account"

    @patch(
        "datahub.ingestion.source.snowflake.snowflake_connection.SnowflakeConnectionConfig.get_native_connection"
    )
    def test_snowflake_connection(self, mock_get_connection, mock_config, mock_pipeline_context):
        """Test Snowflake connection is created using DataHub's connection config"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_connection.return_value = mock_conn

        config = GlossaryExportConfig.model_validate(mock_config)
        action = GlossaryExportAction(config, mock_pipeline_context)

        conn = action._get_snowflake_connection()
        assert conn is not None
        mock_get_connection.assert_called_once()
        # Verify database and schema were set
        assert mock_cursor.execute.call_count == 2

    def test_transform_glossary_term(self, sample_glossary_term):
        """Test transformation of glossary term to database row"""
        row = transform_entity_to_row(sample_glossary_term)

        assert row is not None
        assert row.urn == "urn:li:glossaryTerm:test-term"
        assert row.name == "Test Term"
        assert row.entity_type == "glossary_term"
        assert row.description == "A test glossary term"
        assert row.parent_node_urn == "urn:li:glossaryNode:finance"
        assert row.parent_node_name == "Finance"
        assert row.hierarchical_path == "Finance > Test Term"
        assert row.domain_urn == "urn:li:domain:finance-domain"
        assert row.domain_name == "Finance Domain"
        assert row.custom_properties == {"classification": "PII", "criticality": "high"}
        assert row.ownership is not None
        assert len(row.ownership) == 1
        assert row.ownership[0]["username"] == "jdoe"
        assert row.ownership[0]["type"] == "TECHNICAL_OWNER"

    def test_transform_glossary_node(self, sample_glossary_node):
        """Test transformation of glossary node to database row"""
        row = transform_entity_to_row(sample_glossary_node)

        assert row is not None
        assert row.urn == "urn:li:glossaryNode:finance"
        assert row.name == "Finance"
        assert row.entity_type == "glossary_node"
        assert row.description == "Finance glossary node"
        assert row.parent_node_urn is None
        assert row.hierarchical_path == "Finance"

    def test_build_hierarchical_path(self):
        """Test building hierarchical path from parent nodes"""
        parent_nodes = {
            "nodes": [
                {"properties": {"name": "Root"}},
                {"properties": {"name": "Level1"}},
                {"properties": {"name": "Level2"}},
            ]
        }

        path = build_hierarchical_path(parent_nodes)
        assert path == "Root > Level1 > Level2"

    def test_build_hierarchical_path_empty(self):
        """Test building hierarchical path with no parents"""
        path = build_hierarchical_path(None)
        assert path == ""

        path = build_hierarchical_path({"nodes": []})
        assert path == ""

    def test_fetch_glossary_terms(self, mock_pipeline_context, sample_glossary_term):
        """Test fetching glossary terms from GraphQL"""
        from action_glossary_export.graphql import fetch_all_glossary_terms

        mock_datahub_graph = MagicMock()
        mock_datahub_graph.execute_graphql.return_value = {
            "search": {
                "total": 1,
                "searchResults": [{"entity": sample_glossary_term}],
            }
        }
        mock_pipeline_context.graph.graph = mock_datahub_graph

        terms = fetch_all_glossary_terms(mock_pipeline_context.graph, batch_size=1000)

        assert len(terms) == 1
        assert terms[0]["urn"] == "urn:li:glossaryTerm:test-term"
        mock_datahub_graph.execute_graphql.assert_called()

    def test_create_table(self):
        """Test table creation in Snowflake"""
        from action_glossary_export.snowflake import create_glossary_table

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        create_glossary_table(mock_conn, "test_glossary_export")

        # Check that table creation SQL was executed
        calls = [str(call) for call in mock_cursor.execute.call_args_list]
        sql_call = next((call for call in calls if "CREATE TABLE" in str(call)), None)
        assert sql_call is not None
        assert "test_glossary_export" in str(sql_call)

    @patch(
        "datahub.ingestion.source.snowflake.snowflake_connection.SnowflakeConnectionConfig.get_native_connection"
    )
    def test_close_connection(self, mock_get_connection, mock_config, mock_pipeline_context):
        """Test closing Snowflake connection"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_connection.return_value = mock_conn

        config = GlossaryExportConfig.model_validate(mock_config)
        action = GlossaryExportAction(config, mock_pipeline_context)
        action._get_snowflake_connection()

        action.close()

        mock_conn.close.assert_called_once()
        assert action.snowflake_conn is None

    def test_act_method(self, mock_config, mock_pipeline_context):
        """Test act method (currently a no-op)"""
        from datahub_actions.event.event_envelope import EventEnvelope

        config = GlossaryExportConfig.model_validate(mock_config)
        action = GlossaryExportAction(config, mock_pipeline_context)

        mock_event = Mock(spec=EventEnvelope)
        mock_event.event_type = "test_event"

        action.act(mock_event)

    def test_create_usage_table(self):
        """Test usage table creation in Snowflake"""
        from action_glossary_export.snowflake import create_usage_table

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        create_usage_table(mock_conn, "datahub_glossary_term_usage")

        # Check that usage table creation SQL was executed
        calls = [str(call) for call in mock_cursor.execute.call_args_list]
        sql_call = next((call for call in calls if "CREATE TABLE" in str(call)), None)
        assert sql_call is not None
        assert "datahub_glossary_term_usage" in str(sql_call)

    def test_transform_usage_dashboard(self, sample_glossary_term, sample_dashboard_entity):
        """Test transformation of glossary term usage with Power BI dashboard"""
        usage_record = {
            "glossary_term_urn": sample_glossary_term["urn"],
            "glossary_term_name": sample_glossary_term["properties"]["name"],
            "entity": sample_dashboard_entity,
        }

        row = transform_usage_to_row(usage_record)

        assert row is not None
        assert row.glossary_term_urn == "urn:li:glossaryTerm:test-term"
        assert row.glossary_term_name == "Test Term"
        assert row.entity_urn == "urn:li:dashboard:(powerbi,sales-dashboard)"
        assert row.entity_name == "Sales Dashboard"
        assert row.entity_type == "dashboard"
        assert row.entity_subtype == "Report"
        assert row.platform == "powerbi"
        assert row.container_urn == "urn:li:container:workspace123"
        assert row.container_name == "Sales Workspace"
        assert row.domain_urn == "urn:li:domain:sales-domain"
        assert row.domain_name == "Sales Domain"

    def test_transform_usage_dataset(self, sample_glossary_term, sample_dataset_entity):
        """Test transformation of glossary term usage with Snowflake dataset"""
        usage_record = {
            "glossary_term_urn": sample_glossary_term["urn"],
            "glossary_term_name": sample_glossary_term["properties"]["name"],
            "entity": sample_dataset_entity,
        }

        row = transform_usage_to_row(usage_record)

        assert row is not None
        assert row.glossary_term_urn == "urn:li:glossaryTerm:test-term"
        assert row.glossary_term_name == "Test Term"
        assert row.entity_type == "dataset"
        assert row.entity_subtype == "Table"
        assert row.platform == "snowflake"
        assert row.domain_name == "Analytics"

    def test_fetch_glossary_term_usage(
        self, mock_pipeline_context, sample_dashboard_entity, sample_dataset_entity
    ):
        """Test fetching entities that use a glossary term"""
        from action_glossary_export.graphql import fetch_glossary_term_usage

        mock_datahub_graph = MagicMock()
        mock_datahub_graph.execute_graphql.return_value = {
            "searchAcrossEntities": {
                "total": 2,
                "searchResults": [
                    {"entity": sample_dashboard_entity},
                    {"entity": sample_dataset_entity},
                ],
            }
        }
        mock_pipeline_context.graph.graph = mock_datahub_graph

        entities = fetch_glossary_term_usage(
            mock_pipeline_context.graph, "urn:li:glossaryTerm:test-term", ["DASHBOARD", "DATASET"]
        )

        assert len(entities) == 2
        assert entities[0]["type"] == "DASHBOARD"
        assert entities[1]["type"] == "DATASET"
        mock_datahub_graph.execute_graphql.assert_called()

    def test_fetch_all_glossary_term_usage(
        self, mock_pipeline_context, sample_glossary_term, sample_dashboard_entity
    ):
        """Test fetching usage for all glossary terms"""
        from action_glossary_export.graphql import fetch_all_glossary_term_usage

        mock_datahub_graph = MagicMock()
        mock_datahub_graph.execute_graphql.return_value = {
            "searchAcrossEntities": {
                "total": 1,
                "searchResults": [
                    {"entity": sample_dashboard_entity},
                ],
            }
        }
        mock_pipeline_context.graph.graph = mock_datahub_graph

        usage_records = fetch_all_glossary_term_usage(
            mock_pipeline_context.graph, [sample_glossary_term], ["DASHBOARD"]
        )

        assert len(usage_records) == 1
        assert usage_records[0]["glossary_term_urn"] == "urn:li:glossaryTerm:test-term"
        assert usage_records[0]["glossary_term_name"] == "Test Term"
        assert usage_records[0]["entity"]["type"] == "DASHBOARD"

    def test_insert_usage_rows(self):
        """Test inserting usage rows to Snowflake"""
        from action_glossary_export.models import UsageRow
        from action_glossary_export.snowflake import insert_usage_rows

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        usage_rows = [
            UsageRow(
                glossary_term_urn="urn:li:glossaryTerm:test-term",
                glossary_term_name="Test Term",
                entity_urn="urn:li:dashboard:(powerbi,sales)",
                entity_name="Sales Dashboard",
                entity_type="dashboard",
                entity_subtype="Report",
                platform="powerbi",
                container_urn="urn:li:container:workspace",
                container_name="Workspace",
                domain_urn="urn:li:domain:sales",
                domain_name="Sales",
            )
        ]

        insert_usage_rows(mock_conn, "test_usage_table", usage_rows)

        # Verify TRUNCATE was called
        truncate_calls = [
            call for call in mock_cursor.execute.call_args_list if "TRUNCATE" in str(call)
        ]
        assert len(truncate_calls) == 1

        # Verify INSERT was called
        insert_calls = [
            call for call in mock_cursor.execute.call_args_list if "INSERT" in str(call)
        ]
        assert len(insert_calls) == 1

        # Verify commit was called
        mock_conn.commit.assert_called_once()

    def test_config_usage_table_name_default(self):
        """Test default usage table name in config"""
        minimal_config = {
            "connection": {
                "account_id": "test",
                "username": "test",
                "password": "test",
            },
            "destination": {
                "database": "test",
                "schema": "test",
            },
        }
        config = GlossaryExportConfig.model_validate(minimal_config)
        assert config.destination.usage_table_name == "datahub_glossary_term_usage"

    def test_config_entity_types_custom(self):
        """Test custom entity_types configuration"""
        config_dict = {
            "connection": {
                "account_id": "test",
                "username": "test",
                "password": "test",
            },
            "destination": {
                "database": "test",
                "schema": "test",
            },
            "entity_types": ["DASHBOARD", "CHART", "DATASET"],
        }
        config = GlossaryExportConfig.model_validate(config_dict)
        assert config.entity_types == ["DASHBOARD", "CHART", "DATASET"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
