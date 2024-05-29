import unittest
from unittest.mock import patch, MagicMock
from analysis import run_analysis, preprocess_text, load_files_from_folder

class TestAnalysis(unittest.TestCase):

    def test_preprocess_text(self):
        text = "Hello, World!"
        result = preprocess_text(text)
        self.assertEqual(result, "hello, world!")

    @patch('os.listdir')
    @patch('os.path.join')
    @patch('docx.Document')
    def test_load_files_from_folder(self, mock_document, mock_path_join, mock_listdir):
        mock_listdir.return_value = ['file1.docx', 'file2.docx']
        mock_path_join.side_effect = lambda folder, filename: f"{folder}/{filename}"
        mock_doc_instance = MagicMock()
        mock_doc_instance.paragraphs = [MagicMock(text="Text in file1")]
        mock_document.return_value = mock_doc_instance

        result = load_files_from_folder('test_folder')
        self.assertEqual(len(result), 2)
        self.assertIn('file1.docx', result)
        self.assertEqual(result['file1.docx'], 'text in file1')

    @patch('database.save_history')
    @patch('analysis.load_files_from_folder')
    @patch('analysis.train_tfidf_model')
    @patch('analysis.calculate_similarity')
    @patch('analysis.calculate_originality')
    @patch('analysis.calculate_self_similarity')
    def test_run_analysis(self, mock_calc_self_sim, mock_calc_orig, mock_calc_sim, mock_train_tfidf, mock_load_files, mock_save_history):
        mock_load_files.return_value = {
            'file1.docx': 'text in file1',
            'file2.docx': 'text in file2'
        }
        mock_train_tfidf.return_value = (MagicMock(), MagicMock())
        mock_calc_sim.return_value = [[0.1, 0.2]]
        mock_calc_orig.return_value = [[0.9, 0.8]]
        mock_calc_self_sim.return_value = 0.05

        results, overall_results = run_analysis('query_file.docx', 'test_folder', 'test_user')

        self.assertEqual(len(results), 2)
        self.assertIn('Similarity', results.columns)
        self.assertIn('Originality', results.columns)
        self.assertAlmostEqual(overall_results['average_originality'], 90)
        self.assertAlmostEqual(overall_results['average_citation'], 10)
        self.assertAlmostEqual(overall_results['self_plagiarism'], 5)

if __name__ == '__main__':
    unittest.main()
