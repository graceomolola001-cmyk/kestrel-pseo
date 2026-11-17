import tempfile
import unittest
from pathlib import Path
from seo_ops.experiments import evaluate, plan_sample_size
from seo_ops.refresh import create_refresh_queue


class TestExperiments(unittest.TestCase):
    def test_plan_positive(self):
        self.assertGreater(plan_sample_size(.04, .20), 1000)

    def test_small_sample_inconclusive_even_with_lift(self):
        result = evaluate(100, 4, 100, 20, 3000)
        self.assertFalse(result['sample_requirement_met'])
        self.assertIn('inconclusive', result['conclusion'])

    def test_no_difference_inconclusive(self):
        result = evaluate(2000,100,2000,100,2000)
        self.assertIn('inconclusive', result['conclusion'])

    def test_bad_conversion_counts(self):
        with self.assertRaises(ValueError): evaluate(5,10,5,1,5)

    def test_human_review_queue(self):
        with tempfile.TemporaryDirectory() as tmp:
            src=Path(tmp)/'a.csv'; dst=Path(tmp)/'b.csv'
            src.write_text('page,clicks,impressions,ctr,position\n/a,20,2000,0.01,9\n',encoding='utf-8')
            rows=create_refresh_queue(str(src),str(dst))
            self.assertEqual(rows[0]['approval'], 'PENDING_HUMAN_REVIEW')
            self.assertTrue(dst.exists())


if __name__=='__main__':unittest.main()
