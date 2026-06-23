## ADDED Requirements

### Requirement: Custom model provider configuration

The system SHALL allow users to add, edit, and delete custom OpenAI-compatible model providers (both LLM and Embedding) through the frontend UI.

#### Scenario: Add custom LLM provider
- **WHEN** user enters base_url, api_key, model_name, and provider name in the settings UI and saves
- **THEN** the provider is stored in the database with api_key encrypted via Fernet
- **AND** the provider appears in the provider selection dropdown

#### Scenario: Delete custom provider
- **WHEN** user deletes a custom (non-preset) provider
- **THEN** the provider is removed from the database and dropdown

#### Scenario: Cannot delete preset providers
- **WHEN** user attempts to delete a preset provider (is_preset=true)
- **THEN** the system returns an error indicating preset providers cannot be deleted

### Requirement: Dynamic provider switching without restart

The system SHALL apply provider changes immediately without requiring a backend restart.

#### Scenario: Switch active LLM provider
- **WHEN** user selects a different LLM provider and saves
- **THEN** all subsequent `/ask` requests use the new provider's configuration
- **AND** no backend restart is required

#### Scenario: Switch active Embedding provider
- **WHEN** user selects a different Embedding provider and saves
- **THEN** subsequent document ingestion and retrieval use the new provider

### Requirement: Provider connection test

The system SHALL allow users to test a provider's connection before activation.

#### Scenario: Test valid connection
- **WHEN** user clicks "Test Connection" with valid base_url and api_key
- **THEN** the system calls `GET {base_url}/models` and returns "Connection successful" with available model count

#### Scenario: Test invalid connection
- **WHEN** user clicks "Test Connection" with invalid credentials
- **THEN** the system returns a specific error message (e.g., "401 Unauthorized" or "Connection timeout")
- **AND** an error is shown within 5 seconds

### Requirement: API key encryption at rest

The system SHALL encrypt all stored API keys using Fernet symmetric encryption.

#### Scenario: API key stored encrypted
- **WHEN** user saves a provider with an API key
- **THEN** the api_key is encrypted before being written to the database

#### Scenario: API key masked in responses
- **WHEN** the API returns provider details
- **THEN** the api_key field shows only the last 4 characters (e.g., "sk-...abc1")

#### Scenario: Missing encryption key handled
- **WHEN** `FERNET_KEY` is not set on first startup
- **THEN** the system auto-generates a new Fernet key and writes it to `.env`

### Requirement: Preset provider recommendations

The system SHALL provide a curated list of preset model providers with pre-filled base_url and model_name.

#### Scenario: Presets loaded on first startup
- **WHEN** the database is initialized for the first time
- **THEN** preset providers (智谱, DeepSeek, OpenAI, Groq, Ollama for LLM; 智谱, OpenAI, SiliconFlow, local for Embedding) are inserted with preset=true

#### Scenario: Preset fields are partially read-only in UI
- **WHEN** user selects a preset provider
- **THEN** base_url and model_name are displayed but not editable
- **AND** api_key field remains editable for user input

### Requirement: Embedding provider supports custom configuration

The system SHALL support custom Embedding providers through the same provider configuration system.

#### Scenario: Custom Embedding provider
- **WHEN** user adds an Embedding provider with base_url, api_key, model_name
- **THEN** the system creates an OpenAI-compatible embeddings client for document vectorization

#### Scenario: Local Embedding as special case
- **WHEN** the "local-emb" preset is selected
- **THEN** the system uses HuggingFaceEmbeddings locally without making API calls
