import os
import shutil
from pathlib import Path
import unittest
from unittest import TestCase, mock
from DigiSModEditor.core import create_project_mods_structure


class TestCreateProjectStructure(TestCase):
    def setUp(self):
        self.project_name = 'test_project'
        self.dir_path = Path(os.getcwd())
        self.non_existent_dir = Path(os.getcwd()) / 'non_existent_dir'

    def test_create_project_structure_in_current_directory(self):
        project_dir = create_project_mods_structure(self.project_name, self.dir_path)
        self.assertTrue(project_dir.exists())
        self.assertTrue((project_dir / 'modfiles').exists())
        self.assertEqual(project_dir.name, self.project_name)

    def test_create_project_structure_raises_exception_when_project_name_is_empty(self):
        with self.assertRaises(ValueError):
            create_project_mods_structure('', self.dir_path)

    def test_create_project_structure_creates_project_structure_in_specified_directory(self):
        project_name = 'test_project'
        dir_path = Path(os.getcwd()) / 'test_dir'
        dir_path.mkdir(exist_ok=True)

        project_dir = create_project_mods_structure(project_name, dir_path)

        self.assertTrue(project_dir.exists())
        self.assertTrue((project_dir / 'modfiles').exists())
        self.assertEqual(project_dir.name, project_name)

        # Clean up after the test
        shutil.rmtree(dir_path)

    def test_create_project_structure_creates_modfiles_directory(self):
        project_dir = create_project_mods_structure(self.project_name, self.dir_path)
        mod_dir = project_dir / 'modfiles'
        self.assertTrue(mod_dir.exists())

    @mock.patch('os.path.exists', return_value = False)
    def test_create_project_structure_raises_exception_when_directory_does_not_exist(self, mock_exists):
        with self.assertRaises(FileNotFoundError):
            create_project_mods_structure(self.project_name, self.non_existent_dir)

    def test_create_project_structure_does_not_create_modfiles_directory_if_it_already_exists(self):
        project_name = 'test_project'
        dir_path = Path(os.getcwd()) / 'test_dir'
        dir_path.mkdir(exist_ok=True)

        project_dir = create_project_mods_structure(project_name, dir_path)
        mod_dir = project_dir / 'modfiles'
        mod_dir.mkdir(exist_ok=True)  # Create the 'modfiles' directory manually

        create_project_mods_structure(project_name, dir_path)  # Call the function again

        self.assertTrue(project_dir.exists())
        self.assertTrue(mod_dir.exists())  # The 'modfiles' directory should still exist

        # Clean up after the test
        shutil.rmtree(dir_path)


if __name__ == '__main__':
    unittest.main()
    
    