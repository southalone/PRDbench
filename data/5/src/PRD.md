Certainly! Here is the English translation of your Markdown, with the format preserved:

---

### Product Requirement Document (PRD) Template and Auto-generation Tool

#### 1. Requirement Overview
This tool is designed to provide a complete workflow, from creating product requirement templates via command-line interaction, to automatically generating product documentation based on these templates. Users can define structured requirement templates that include specifications for image resources and product feature requirements, then upload or specify image resources that align with the template. The system automatically extracts image features (e.g., dominant color, style tags) and combines this information with the template to generate standardized product PRD documentation. The tool needs to integrate image processing, feature engineering, and document generation capabilities to ensure the output meets project management standards and product development requirements. README files and unit tests should also be provided.

#### 2. Basic Functional Requirements

##### 2.1 Product Requirement Template Generation Module

- **Template Fields**: Must include the following required fields:

  - Basic Information (Product Name, Target Users)
  - Image Resource Specification (Source Type: Local Path; Allowed File Types: JPG/PNG/jpeg/WebP)
  - Product Feature Requirements (Style Keywords: e.g., "Minimalist", "Retro"; Color Emotional Tendency: e.g., "Cool Tone - Professional", "Warm Tone - Affinity," must align with psychological color emotion theory)

- **Template Validation and Saving**: Validate user input for field completeness (required fields non-empty) and file type validity (MIME type verification). Upon passing validation, save to the specified path in JSON format, supporting template naming and overwrite confirmation.

##### 2.2 Image Resource Processing Module

- **Resource Import and Validation**: Users can specify local image paths; the system automatically checks:
  - If the source type matches "Image Resource Specification - Source Type" in the template
  - If the file type is in the allowed list of the template (verify actual type by reading file header bytes to prevent extension spoofing)

- **Image Preprocessing**: For validated images, standardized processing includes:
  - Format Conversion (convert to the template's preferred file format)
  - Metadata Cleaning (remove sensitive data such as location information in EXIF metadata)

##### 2.3 Product Feature Extraction Module

- **Visual Feature Extraction**: Based on preprocessed images, use OpenCV to extract the following features:
  - Dominant Color Analysis: Convert RGB color space to HSV, use K-means clustering algorithm (k=5) to extract the top 3 dominant colors, output color values (HEX format) and proportions
  - Texture Feature Extraction: Calculate image LBP (Local Binary Pattern) histogram to generate "fine/coarse" texture tags

- **Style Description Generation**: Users need to enter a large language model API key (e.g., OpenAI API Key); the system calls the API and provides:
  - "Style Keywords" and "Color Emotional Tendency" from the template
  - Extracted dominant color and texture tags
  - Generates a product visual style description text complying with the AIDA model (Attention-Interest-Desire-Action), limited to 200 characters

##### 2.4 Product PRD Document Generation Module

- **Document Structure Integration**: Generate a Markdown-format PRD document using the following fixed structure:
  - Product Overview (from the template's basic information)
  - Image Resource Specifications (including processed image paths)
  - Core Feature Descriptions (visual feature data + style description text)
  - Development Schedule Suggestions (based on the Critical Path Method - CPM, dividing into "image processing - feature extraction - document generation" three nodes; estimating time for each and total duration)

- **Document Output**: Support specifying an output path, prompt with "Document generation complete, path: [user-specified path]".

##### 2.5 Command-line Interaction and Validation Module

- **Menu Navigation**: Show the main menu on tool startup, allowing users to choose:
  1. Create/Edit Requirement Template
  2. Generate Product PRD Based on Template
  3. Exit Tool

- **Input Validation**: Perform legal checks on all user input, including:
  - Path/URL Format (local paths must verify file existence; URLs must check HTTP status code 200)
  - API Key Format (e.g., OpenAI key must match regex ^sk-[A-Za-z0-9]{48}$)
  - Numeric Input (e.g., k-means cluster number) must be a positive integer

- **Error Handling**: On input errors, display error messages in Chinese (e.g., "Unable to find an image in this local path"), support user re-input, and prevent program crashes.

---