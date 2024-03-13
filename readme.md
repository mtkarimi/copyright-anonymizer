# Text Anonymizer for LLMs 📖🔓

## Introduction
Emerging from a critical exploration of copyright laws and the rapid advancement of Large Language Models (LLMs), the Text Anonymizer project addresses LLMs' often indifferent processing of copyrighted text. This tool, while not revolutionary, serves as a focused effort to spotlight the crucial need for copyright respect in the AI era. It illustrates how easily text can be anonymized to bypass copyright detection using simple tools, yet underscores the importance of a more thoughtful approach to content creation and usage. Created specifically to emphasize ethical AI development and the careful handling of copyrighted materials, the Text Anonymizer app champions the necessity of ethical guidelines in AI application, particularly in how LLMs handle copyrighted content.

## Core Philosophy
The project is rooted in a simple yet profound premise: awareness and respect for copyright should be integral to the development and application of AI technologies, especially LLMs. By providing a straightforward mechanism to anonymize text—replacing key identifiers like author names and publishing details—this tool serves as a wake-up call to the community. It highlights how effortlessly copyrighted content can be repurposed without due acknowledgment, stressing the need for ethical guidelines and copyright-aware AI development.

## Features and Functionality
- **Simplistic Yet Powerful**: Offers an easy-to-use interface for anonymizing text, demonstrating the potential misuse of LLMs in disregarding copyright.
- **An Ethical Framework**: By facilitating discussions around the ethical use of LLMs, it encourages users to consider the implications of anonymizing text for copyright evasion.
- **Versatility**: While illustrating a point, it also provides practical utility for legitimate use cases requiring anonymization for privacy or security reasons.

## How to Use the Text Anonymizer

### Getting Started
1. **Visit the Application**: Open the Streamlit application link in your web browser to access the Text Anonymizer interface.
2. **Upload Your Text**: Use the file uploader to select the text file you wish to anonymize. The tool accepts `.txt` files.

### Anonymizing Your Text
1. **Set Preferences**: Adjust the processing parameters according to your needs. You can specify chunk sizes, processing coverage, and chunk overlap sizes for optimal results.
2. **Enter Keywords for Anonymization**: If there are specific words or phrases you wish to anonymize, enter them in the provided text area.
3. **Select Target Entity Types**: Choose the types of entities you want the tool to anonymize, such as people or companies.
4. **Start Anonymization**: Click the "Start Anonymization" button to begin the process. The tool will then process your text, anonymizing it based on your specifications.

### Downloading and Modifying
1. **Download Anonymized Text**: Once the process is complete, a download button will appear, allowing you to save the anonymized text along with any keys to your device.
2. **Make Adjustments**: If necessary, you can modify the replacements directly in the application for better accuracy or personalization.

### Reverse Anonymization (Optional)
1. **Upload Anonymized Text and Keys**: If you wish to reverse the anonymization, upload the anonymized text file and the keys file in the "Reverse Anonymization" tab.
2. **Download the Reversed Text**: After uploading, you can download the text with the original content restored using the provided keys.

## Acknowledgements
This project leverages the following tools and libraries, without which it would not have been possible:

- **[Streamlit](https://streamlit.io/)**: For its user-friendly web application framework that made building and deploying this tool a seamless process.
- **[spaCy](https://spacy.io/)**: For its powerful natural language processing capabilities that drive the core functionality of the Text Anonymizer.
- **[annotated_text](https://github.com/tvst/annotated-text)**: For enabling the visual representation of annotations within Streamlit, enhancing user interaction with the anonymized text.
- **[LangChain](https://www.langchain.com/)**: For their insights and contributions to the domain of language models and AI applications. Their work in making AI technologies more accessible and ethical has been an invaluable source of inspiration for this project.

A heartfelt thanks to the developers and contributors of these tools for their dedication to open source. Their work has not only made this project possible but also continues to inspire and enable countless other projects in the realm of AI and beyond.
