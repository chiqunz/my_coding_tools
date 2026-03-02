---
name: dotnet-project-setup
description: Bootstrap the .NET project dev environment — generate .vscode/settings.json, .vscode/extensions.json, .editorconfig, and verify tooling is installed.
triggers:
  - "setup project"
  - "init project"
  - "bootstrap"
  - "setup vscode"
  - "configure editor"
  - "setup dev environment"
tools:
  - Bash
  - Read
  - Write
  - Glob
---

# .NET Project Setup Skill

## When Triggered

Bootstrap or verify the .NET project dev environment. Generate editor configuration files if missing.

## Steps

### 1. Check and create `.vscode/settings.json`

Check if `.vscode/settings.json` exists. If missing, create the `.vscode/` directory and write the settings file with these exact values:

```json
{
  "editor.formatOnSave": true,
  "editor.formatOnType": true,
  "editor.rulers": [120],
  "editor.tabSize": 4,
  "editor.insertSpaces": true,
  "editor.bracketPairColorization.enabled": true,
  "editor.guides.bracketPairs": "active",

  "files.trimTrailingWhitespace": true,
  "files.insertFinalNewline": true,
  "files.trimFinalNewlines": true,
  "files.exclude": {
    "**/bin": true,
    "**/obj": true,
    "**/.vs": true,
    "**/TestResults": true,
    "**/*.user": true
  },

  "[csharp]": {
    "editor.defaultFormatter": "ms-dotnettools.csharp",
    "editor.formatOnSave": true,
    "editor.formatOnType": true,
    "editor.codeActionsOnSave": {
      "source.fixAll": "explicit",
      "source.organizeImports": "explicit"
    },
    "editor.tabSize": 4
  },

  "[json]": {
    "editor.defaultFormatter": "vscode.json-language-features",
    "editor.formatOnSave": true,
    "editor.tabSize": 2
  },

  "omnisharp.enableRoslynAnalyzers": true,
  "omnisharp.enableEditorConfigSupport": true,
  "omnisharp.organizeImportsOnFormat": true,
  "omnisharp.enableImportCompletion": true,

  "dotnet.completion.showCompletionItemsFromUnimportedNamespaces": true,
  "dotnet.inlayHints.enableInlayHintsForParameters": true,
  "dotnet.inlayHints.enableInlayHintsForLiteralParameters": true,
  "dotnet.inlayHints.suppressInlayHintsForParametersThatMatchMethodIntent": true,
  "dotnet.inlayHints.suppressInlayHintsForParametersThatMatchArgumentName": true,

  "csharp.format.enable": true,

  "terminal.integrated.env.linux": {
    "DOTNET_CLI_TELEMETRY_OPTOUT": "1",
    "DOTNET_NOLOGO": "1"
  },
  "terminal.integrated.env.osx": {
    "DOTNET_CLI_TELEMETRY_OPTOUT": "1",
    "DOTNET_NOLOGO": "1"
  },
  "terminal.integrated.env.windows": {
    "DOTNET_CLI_TELEMETRY_OPTOUT": "1",
    "DOTNET_NOLOGO": "1"
  },

  "search.exclude": {
    "**/bin": true,
    "**/obj": true,
    "**/.vs": true,
    "**/Migrations/*.Designer.cs": true
  }
}
```

If it already exists, verify the key settings (C# formatter, format on save, Roslyn analyzers enabled). Add any missing keys without overwriting existing customizations.

### 2. Check and create `.vscode/extensions.json`

If missing, create with:

```json
{
  "recommendations": [
    "ms-dotnettools.csharp",
    "ms-dotnettools.csdevkit",
    "ms-dotnettools.vscode-dotnet-runtime",
    "ms-dotnettools.vscodeintellicode-csharp",
    "formulahendry.dotnet-test-explorer",
    "patcx.vscode-nuget-gallery",
    "humao.rest-client",
    "redhat.vscode-xml",
    "EditorConfig.EditorConfig",
    "usernamehw.errorlens",
    "eamodio.gitlens",
    "ms-azuretools.vscode-docker"
  ]
}
```

### 3. Check and create `.editorconfig`

Check if `.editorconfig` exists at the repo root. If missing, create it with the full C# code style rules:

```ini
root = true

[*]
charset = utf-8
end_of_line = lf
indent_style = space
indent_size = 4
insert_final_newline = true
trim_trailing_whitespace = true

[*.{xml,csproj,props,targets,config,nuspec,resx}]
indent_size = 2

[*.{json,jsonc}]
indent_size = 2

[*.{yml,yaml}]
indent_size = 2

[*.md]
trim_trailing_whitespace = false

[*.cs]
indent_size = 4

# Organize Usings
dotnet_sort_system_directives_first = true
dotnet_separate_import_directive_groups = false

# this. preferences
dotnet_style_qualification_for_field = false:warning
dotnet_style_qualification_for_property = false:warning
dotnet_style_qualification_for_method = false:warning
dotnet_style_qualification_for_event = false:warning

# Language keywords vs BCL types
dotnet_style_predefined_type_for_locals_parameters_members = true:warning
dotnet_style_predefined_type_for_member_access = true:warning

# var preferences
csharp_style_var_for_built_in_types = true:suggestion
csharp_style_var_when_type_is_apparent = true:suggestion
csharp_style_var_elsewhere = true:suggestion

# Expression-bodied members
csharp_style_expression_bodied_methods = when_on_single_line:suggestion
csharp_style_expression_bodied_constructors = false:suggestion
csharp_style_expression_bodied_properties = true:suggestion
csharp_style_expression_bodied_accessors = true:suggestion
csharp_style_expression_bodied_lambdas = true:suggestion
csharp_style_expression_bodied_local_functions = when_on_single_line:suggestion

# Pattern matching
csharp_style_pattern_matching_over_is_with_cast_check = true:warning
csharp_style_pattern_matching_over_as_with_null_check = true:warning

# Null checking
dotnet_style_coalesce_expression = true:warning
dotnet_style_null_propagation = true:warning
dotnet_style_prefer_is_null_check_over_reference_equality_method = true:warning
csharp_style_throw_expression = true:suggestion
csharp_style_conditional_delegate_call = true:suggestion

# Modifier preferences
dotnet_style_require_accessibility_modifiers = for_non_interface_members:warning

# File-scoped namespaces
csharp_style_namespace_declarations = file_scoped:warning

# Primary constructors
csharp_style_prefer_primary_constructors = true:suggestion

# Collection expressions
dotnet_style_prefer_collection_expression = true:suggestion

# Braces
csharp_prefer_braces = when_multiline:suggestion

# Using placement
csharp_using_directive_placement = outside_namespace:warning

# New line preferences
csharp_new_line_before_open_brace = all
csharp_new_line_before_else = true
csharp_new_line_before_catch = true
csharp_new_line_before_finally = true

# Naming — PascalCase for public
dotnet_naming_rule.public_members_must_be_pascal_case.severity = warning
dotnet_naming_rule.public_members_must_be_pascal_case.symbols = public_symbols
dotnet_naming_rule.public_members_must_be_pascal_case.style = pascal_case_style
dotnet_naming_symbols.public_symbols.applicable_kinds = property,method,field,event,delegate
dotnet_naming_symbols.public_symbols.applicable_accessibilities = public,internal,protected
dotnet_naming_style.pascal_case_style.capitalization = pascal_case

# Naming — _camelCase for private fields
dotnet_naming_rule.private_fields_must_be_camel_case.severity = warning
dotnet_naming_rule.private_fields_must_be_camel_case.symbols = private_fields
dotnet_naming_rule.private_fields_must_be_camel_case.style = underscore_camel_case
dotnet_naming_symbols.private_fields.applicable_kinds = field
dotnet_naming_symbols.private_fields.applicable_accessibilities = private
dotnet_naming_style.underscore_camel_case.required_prefix = _
dotnet_naming_style.underscore_camel_case.capitalization = camel_case

# Naming — I prefix for interfaces
dotnet_naming_rule.interfaces_must_start_with_i.severity = warning
dotnet_naming_rule.interfaces_must_start_with_i.symbols = interfaces
dotnet_naming_rule.interfaces_must_start_with_i.style = i_prefix_style
dotnet_naming_symbols.interfaces.applicable_kinds = interface
dotnet_naming_style.i_prefix_style.required_prefix = I
dotnet_naming_style.i_prefix_style.capitalization = pascal_case

# Nullable reference type diagnostics
dotnet_diagnostic.CS8600.severity = warning
dotnet_diagnostic.CS8601.severity = warning
dotnet_diagnostic.CS8602.severity = warning
dotnet_diagnostic.CS8603.severity = warning
dotnet_diagnostic.CS8604.severity = warning
dotnet_diagnostic.CS8618.severity = warning
dotnet_diagnostic.CS8625.severity = warning

# IDE analyzers
dotnet_diagnostic.IDE0005.severity = warning
dotnet_diagnostic.IDE0055.severity = warning
dotnet_diagnostic.IDE0161.severity = warning
```

If it already exists, verify the critical rules are present (file-scoped namespaces, naming conventions, nullable diagnostics). Add any missing rules without overwriting existing ones.

### 4. Verify tooling is available

Run these checks and report status:

```bash
# Check .NET SDK version
dotnet --version

# Check SDK list
dotnet --list-sdks

# Verify solution file exists
ls *.sln 2>/dev/null || echo "WARNING: No .sln file found"

# Verify it builds
dotnet build --verbosity quiet

# Check EF Core tools
dotnet ef --version 2>/dev/null || echo "EF Core tools not installed — run: dotnet tool install --global dotnet-ef"
```

### 5. Check for Nullable Reference Types

Scan `Directory.Build.props` or `.csproj` files for `<Nullable>enable</Nullable>`. If not found, warn the user that Nullable Reference Types should be enabled.

### 6. Summary

Report what was created/verified:
- `.vscode/settings.json` — created / already existed / updated
- `.vscode/extensions.json` — created / already existed
- `.editorconfig` — created / already existed / updated
- .NET SDK version
- Solution build status
- Nullable Reference Types status
- EF Core tools status
- Any issues found
