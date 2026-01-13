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

from action_glossary_export.glossary_export_action import (
    GlossaryExportAction,
    GlossaryExportConfig,
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

    def test_transform_glossary_term(
        self, mock_config, mock_pipeline_context, sample_glossary_term
    ):
        """Test transformation of glossary term to database row"""
        config = GlossaryExportConfig.model_validate(mock_config)
        action = GlossaryExportAction(config, mock_pipeline_context)

        row = action._transform_entity_to_row(sample_glossary_term)

        assert row is not None
        assert row["urn"] == "urn:li:glossaryTerm:test-term"
        assert row["name"] == "Test Term"
        assert row["entity_type"] == "glossary_term"
        assert row["description"] == "A test glossary term"
        assert row["parent_node_urn"] == "urn:li:glossaryNode:finance"
        assert row["parent_node_name"] == "Finance"
        assert row["hierarchical_path"] == "Finance > Test Term"
        assert row["domain_urn"] == "urn:li:domain:finance-domain"
        assert row["domain_name"] == "Finance Domain"
        assert row["custom_properties"] == {"classification": "PII", "criticality": "high"}
        assert len(row["ownership"]) == 1
        assert row["ownership"][0]["username"] == "jdoe"
        assert row["ownership"][0]["type"] == "TECHNICAL_OWNER"

    def test_transform_glossary_node(
        self, mock_config, mock_pipeline_context, sample_glossary_node
    ):
        """Test transformation of glossary node to database row"""
        config = GlossaryExportConfig.model_validate(mock_config)
        action = GlossaryExportAction(config, mock_pipeline_context)

        row = action._transform_entity_to_row(sample_glossary_node)

        assert row is not None
        assert row["urn"] == "urn:li:glossaryNode:finance"
        assert row["name"] == "Finance"
        assert row["entity_type"] == "glossary_node"
        assert row["description"] == "Finance glossary node"
        assert row["parent_node_urn"] is None
        assert row["hierarchical_path"] == "Finance"

    def test_build_hierarchical_path(self, mock_config, mock_pipeline_context):
        """Test building hierarchical path from parent nodes"""
        config = GlossaryExportConfig.model_validate(mock_config)
        action = GlossaryExportAction(config, mock_pipeline_context)

        parent_nodes = {
            "nodes": [
                {"properties": {"name": "Root"}},
                {"properties": {"name": "Level1"}},
                {"properties": {"name": "Level2"}},
            ]
        }

        path = action._build_hierarchical_path(parent_nodes)
        assert path == "Root > Level1 > Level2"

    def test_build_hierarchical_path_empty(self, mock_config, mock_pipeline_context):
        """Test building hierarchical path with no parents"""
        config = GlossaryExportConfig.model_validate(mock_config)
        action = GlossaryExportAction(config, mock_pipeline_context)

        path = action._build_hierarchical_path(None)
        assert path == ""

        path = action._build_hierarchical_path({"nodes": []})
        assert path == ""

    def test_fetch_glossary_terms(self, mock_config, mock_pipeline_context, sample_glossary_term):
        """Test fetching glossary terms from GraphQL"""
        mock_datahub_graph = MagicMock()
        mock_datahub_graph.execute_graphql.return_value = {
            "search": {
                "total": 1,
                "searchResults": [{"entity": sample_glossary_term}],
            }
        }
        mock_pipeline_context.graph.graph = mock_datahub_graph

        config = GlossaryExportConfig.model_validate(mock_config)
        action = GlossaryExportAction(config, mock_pipeline_context)

        terms = action._fetch_all_glossary_terms()

        assert len(terms) == 1
        assert terms[0]["urn"] == "urn:li:glossaryTerm:test-term"
        mock_datahub_graph.execute_graphql.assert_called()

    @patch(
        "datahub.ingestion.source.snowflake.snowflake_connection.SnowflakeConnectionConfig.get_native_connection"
    )
    def test_create_table(self, mock_get_connection, mock_config, mock_pipeline_context):
        """Test table creation in Snowflake"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_connection.return_value = mock_conn

        config = GlossaryExportConfig.model_validate(mock_config)
        action = GlossaryExportAction(config, mock_pipeline_context)

        action._create_table_if_not_exists()

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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
