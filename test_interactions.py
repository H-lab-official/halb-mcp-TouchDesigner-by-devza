import importlib.util
from pathlib import Path
import unittest


class InteractionTests(unittest.TestCase):
    def setUp(self):
        spec=importlib.util.spec_from_file_location('gesture_test',Path(__file__).with_name('interaction_logic.py'))
        self.logic=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.logic)
        self.points={'shoulder_l':(.4,.6),'shoulder_r':(.6,.6),
                     'elbow_l':(.3,.5),'elbow_r':(.7,.5),
                     'wrist_l':(.2,.4),'wrist_r':(.8,.4)}

    def test_stillness_opens_flowers_and_grows_vines(self):
        for _ in range(100):state=self.logic.advance(self.points,.05)
        self.assertEqual(state['stillness'],1.)
        self.assertEqual(state['growth'],1.)
        self.assertEqual(state['left_arm_valid'],1.)

    def test_wave_emits_a_burst_then_decays(self):
        self.logic.advance(self.points,.05)
        moved=dict(self.points,wrist_l=(.5,.85))
        peak=self.logic.advance(moved,.05)['burst']
        self.assertGreater(peak,.5)
        for _ in range(80):state=self.logic.advance(moved,.05)
        self.assertLess(state['burst'],.02)

    def test_hand_height_changes_hue(self):
        low=dict(self.points,wrist_l=(.2,.2),wrist_r=(.8,.2))
        high=dict(self.points,wrist_l=(.2,.9),wrist_r=(.8,.9))
        for _ in range(50):self.logic.advance(low,.05)
        low_hue=self.logic.value('hue')
        for _ in range(50):self.logic.advance(high,.05)
        self.assertGreater(self.logic.value('hue')-low_hue,.3)

    def test_tracking_loss_hides_arms_and_recovery_does_not_burst(self):
        self.logic.advance(self.points,.05)
        state=self.logic.advance({},.05)
        self.assertEqual(state['tracked'],0.)
        self.assertEqual(state['left_arm_valid'],0.)
        recovered=self.logic.advance(self.points,.05)
        self.assertEqual(recovered['burst'],0.)


if __name__=='__main__':unittest.main()
