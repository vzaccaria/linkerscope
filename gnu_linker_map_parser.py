import re
import yaml

from section import Section


class GNULinkerMapParser:
    """
    Parse a GNU linker map file and convert it to a yaml file for further processing
    """
    # Pre-compile regex patterns as class attributes for efficiency
    AREAS_PATTERN = re.compile(r'([.][a-z]{1,})[ ]{1,}(0x[a-fA-F0-9]{1,})[ ]{1,}(0x[a-fA-F0-9]{1,})\n')
    SECTIONS_PATTERN = re.compile(
        r'\s(\.[^.\s]+)\.([^\s]+)\n\s+(0x[0-9a-fA-F]{16})\s+(0x[0-9a-fA-F]+)\s+[^\n]+\n'
    )

    def __init__(self, input_filename, output_filename):
        self.sections = []
        self.subsections = []
        self.input_filename = input_filename
        self.output_filename = output_filename

    def parse(self):
        with open(self.input_filename, 'r', encoding='utf8') as file:
            content = file.read()

        # Process areas using finditer on entire content
        for match in self.AREAS_PATTERN.finditer(content):
            self.sections.append(Section(
                parent=None,
                id=match.group(1),
                address=int(match.group(2), 0),
                size=int(match.group(3), 0),
                _type='area'
            ))

        # Process sections using finditer on entire content
        for match in self.SECTIONS_PATTERN.finditer(content):
            self.subsections.append(Section(
                parent=match.group(1),
                id=match.group(2),
                address=int(match.group(3), 0),
                size=int(match.group(4), 0),
                _type='section'
            ))

        my_dict = {'map': []}
        for section in self.sections:
            my_dict['map'].append({
                'type': 'area',
                'address': section.address,
                'size': section.size,
                'id': section.id,
                'flags': section.flags
            })

        for subsection in self.subsections:
            my_dict['map'].append({
                'type': 'section',
                'parent': subsection.parent,
                'address': subsection.address,
                'size': subsection.size,
                'id': subsection.id,
                'flags': subsection.flags
            })

        with open(self.output_filename, 'w', encoding='utf8') as file:
            yaml_string = yaml.dump(my_dict)
            file.write(yaml_string)
