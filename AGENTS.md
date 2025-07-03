# Agent Guidelines for Content Tools Project

This document outlines the coding standards and preferences for AI agents working on this project.

## TypeScript Coding Standards

### Language & Type Preferences
- **Use TypeScript instead of JavaScript**
- **Prefer interfaces over types** for object shapes
- Use UPPERCASE for environment variables

### Function Declarations
- **Use function declarations instead of function expressions** for top-level named functions
- Keep functions short and focused (preferably < 20 lines)
- Maintain a single level of abstraction per function

```typescript
// ✅ Preferred - Function declaration
function processContent(data: ContentData): ProcessedContent {
  return transformData(data);
}

// ❌ Avoid - Function expression
const processContent = (data: ContentData): ProcessedContent => {
  return transformData(data);
};
```

### Variable Naming
- **Prefix boolean variables with verbs**: `is`, `has`, `can`, `should`, etc.
- Avoid magic numbers; define constants using `const`

```typescript
// ✅ Preferred
const isValidContent = checkContent(data);
const hasPermissions = user.permissions.length > 0;
const canEdit = isValidContent && hasPermissions;

const MAX_RETRY_ATTEMPTS = 3;
const DEFAULT_TIMEOUT = 5000;

// ❌ Avoid
const validContent = checkContent(data);
const permissions = user.permissions.length > 0;
const edit = validContent && permissions;

if (retryCount > 3) { // magic number
  // ...
}
```

### Error Handling
- **Return errors instead of panicking** unless it's truly exceptional
- Use proper error types and handle them gracefully

```typescript
// ✅ Preferred
function parseConfig(configPath: string): Result<Config, Error> {
  try {
    const config = loadConfig(configPath);
    return { success: true, data: config };
  } catch (error) {
    return { success: false, error: new Error(`Failed to parse config: ${error.message}`) };
  }
}

// ❌ Avoid
function parseConfig(configPath: string): Config {
  const config = loadConfig(configPath); // This might throw and crash
  return config;
}
```

## Environment Configuration

### Environment Variables
- **Prefer shell environment variables over .env files**
- Use UPPERCASE naming convention for environment variables
- Document required environment variables

```typescript
// ✅ Preferred - Read from shell environment
const API_KEY = process.env.API_KEY;
const DATABASE_URL = process.env.DATABASE_URL;
const PORT = parseInt(process.env.PORT || '3000', 10);

if (!API_KEY) {
  throw new Error('API_KEY environment variable is required');
}
```

### Setting Environment Variables
Prefer setting environment variables in your shell profile or deployment configuration:

```bash
# In your shell profile (.bashrc, .zshrc, config.fish, etc.)
export API_KEY="your-api-key"
export DATABASE_URL="your-database-url"
export NODE_ENV="development"
```

## Interface Design

### Type Definitions
- Use interfaces for object shapes
- Keep interface definitions focused and cohesive
- Use descriptive names that clearly indicate the data structure's purpose

```typescript
// ✅ Preferred
interface ContentMetadata {
  title: string;
  description: string;
  tags: string[];
  createdAt: Date;
  updatedAt: Date;
}

interface ProcessingOptions {
  shouldMinify: boolean;
  includeSourceMaps: boolean;
  outputFormat: 'json' | 'yaml' | 'xml';
}

// ❌ Avoid overly broad or vague interfaces
interface Data {
  stuff: any;
  things: unknown[];
}
```

## Code Organization

### Function Structure
- One function should do one thing well
- Functions should be easily testable
- Avoid deep nesting when possible

```typescript
// ✅ Preferred - Single responsibility, clear purpose
function validateContentStructure(content: unknown): content is ContentData {
  return isObject(content) && 
         hasRequiredFields(content) && 
         hasValidTypes(content);
}

function transformContentToMarkdown(content: ContentData): string {
  const header = generateHeader(content.metadata);
  const body = processBody(content.body);
  return `${header}\n\n${body}`;
}

// ❌ Avoid - Doing too many things
function processEverything(content: unknown): string {
  // validation logic
  // transformation logic  
  // formatting logic
  // all mixed together
}
```

## Project-Specific Guidelines

### Content Processing
- Prefer functional approaches for data transformation
- Use TypeScript's strict type checking to catch errors early
- Implement proper error boundaries for content processing pipelines

### Tool Integration
- When integrating external tools, prefer shell commands over Node.js libraries when appropriate
- Use environment variables for configuration rather than config files
- Implement retry logic for external API calls

## Examples

### Complete Function Example
```typescript
interface ContentProcessingResult {
  success: boolean;
  processedContent?: string;
  error?: string;
}

function processMarkdownContent(
  filePath: string, 
  options: ProcessingOptions
): ContentProcessingResult {
  const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
  
  try {
    const fileStats = getFileStats(filePath);
    const isFileSizeValid = fileStats.size <= MAX_FILE_SIZE;
    
    if (!isFileSizeValid) {
      return {
        success: false,
        error: `File size exceeds maximum allowed size of ${MAX_FILE_SIZE} bytes`
      };
    }
    
    const rawContent = readFileContent(filePath);
    const processedContent = transformMarkdown(rawContent, options);
    
    return {
      success: true,
      processedContent
    };
  } catch (error) {
    return {
      success: false,
      error: `Failed to process markdown: ${error instanceof Error ? error.message : 'Unknown error'}`
    };
  }
}
```

---

*This document should be updated as the project evolves and new patterns emerge.*
