import unittest
from unittest.mock import patch, MagicMock
from gui import display_run_analysis, display_results
from tkinter import Tk

class TestGUI(unittest.TestCase):

    @patch('gui.select_file')
    @patch('gui.select_folder')
    @patch('analysis.run_analysis')
    @patch('gui.display_results')
    def test_display_run_analysis(self, mock_display_results, mock_run_analysis, mock_select_folder, mock_select_file):
        root = Tk()
        content_frame = MagicMock()
        mock_select_file.return_value = 'query_file.docx'
        mock_select_folder.return_value = 'test_folder'
        mock_run_analysis.return_value = (MagicMock(), MagicMock())

        display_run_analysis('test_user')

        mock_display_results.assert_called_once()

    @patch('tkinter.ttk.Treeview')
    def test_display_results(self, mock_treeview):
        root = Tk()
        content_frame = MagicMock()
        results = MagicMock()
        results.columns = ['File', 'Similarity', 'Originality']
        overall_results = {'average_originality': 90, 'average_citation': 10, 'self_plagiarism': 5}

        display_results(results, overall_results, 'test_user')

        self.assertTrue(mock_treeview.called)

if __name__ == '__main__':
    unittest.main()
