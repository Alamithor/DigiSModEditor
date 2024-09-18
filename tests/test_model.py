import unittest
from pathlib import Path
from unittest.mock import patch

from DigiSModEditor.gui.models import create_game_data_model, AsukaModel, create_project_mod_model, AmaterasuModel
from DigiSModEditor import core


class TestCreateGameDataModel(unittest.TestCase):
    def test_raises_exception_if_not_dsdb_directory(self):
        non_existent_dir = Path('/path/to/non/existent/directory')

        with patch.object(core, 'is_dsdb_directory', return_value=False):
            with self.assertRaises(Exception) as context:
                create_game_data_model(non_existent_dir)

            self.assertEqual(str(context.exception), 'Directory does not have *.name files')

    def test_model_instance(self):
        with patch.object(core, 'is_dsdb_directory', return_value=True):
            dsdb_dir_path = Path('/path/to/dsdb/directory')
            model = create_game_data_model(dsdb_dir_path)

            self.assertIsInstance(model, AsukaModel)


class TestCreateProjectModModel(unittest.TestCase):
    def test_raises_exception_if_not_project_mod_directory(self):
        non_project_mod_dir = Path('/path/to/non/project/mod/directory')

        with patch.object(core, 'is_project_mod_directory', return_value=False):
            with self.assertRaises(Exception) as context:
                create_project_mod_model(non_project_mod_dir)

            self.assertEqual(str(context.exception), 'Directory is not project mod directory')

    def test_model_instance(self):
        with patch.object(core, 'is_project_mod_directory', return_value=True):
            with patch.object(core, 'read_metadata_mod') as mock_read_metadata_mod:
                mock_read_metadata_mod.return_value = {
                    'author': 'TestAuthor',
                    'version': (1, 0),
                    'category': 'TestCategory'
                }

                mod_dir_path = Path('/path/to/project/mod/directory')
                model = create_project_mod_model(mod_dir_path)

                self.assertIsInstance(model, AmaterasuModel)
            
    def test_validate_metadata_content(self):
        with patch.object(core, 'is_project_mod_directory', return_value=True):
            with patch.object(core, 'read_metadata_mod') as mock_read_metadata_mod:
                mock_read_metadata_mod.return_value = {
                    'author': 'TestAuthor',
                    'version': (1, 0),
                    'category': 'TestCategory'
                }

                mod_dir_path = Path('/path/to/project/mod/directory')
                model = create_project_mod_model(mod_dir_path)

                mock_read_metadata_mod.assert_called_once_with(mod_dir_path / 'METADATA.json')
                self.assertEqual(model.root_path, mod_dir_path)
                self.assertEqual(model.author, 'TestAuthor')
                self.assertEqual(model.version, (1, 0))
                self.assertEqual(model.category, 'TestCategory')
                
    def test_missing_modfiles_directory(self):
        with patch.object(core, 'is_project_mod_directory', return_value=False):
            with patch.object(core, 'read_metadata_mod') as mock_read_metadata_mod:
                mock_read_metadata_mod.return_value = {
                    'author': 'TestAuthor',
                    'version': (1, 0),
                    'category': 'TestCategory'
                }

                mod_dir_path = Path('/path/to/project/mod/directory')
                with self.assertRaises(FileNotFoundError) as context:
                    create_project_mod_model(mod_dir_path)

                self.assertEqual(str(context.exception), 'Directory is not project mod directory')
                
    def test_missing_metadata_file(self):
        with patch.object(core, 'is_project_mod_directory', return_value=True):
            with patch.object(core, 'read_metadata_mod') as mock_read_metadata_mod:
                mock_read_metadata_mod.side_effect = FileNotFoundError('File not found: METADATA.json')

                mod_dir_path = Path('/path/to/project/mod/directory')
                with self.assertRaises(FileNotFoundError) as context:
                    create_project_mod_model(mod_dir_path)

                self.assertEqual(str(context.exception), 'File not found: METADATA.json')


if __name__ == '__main__':
    unittest.main()
