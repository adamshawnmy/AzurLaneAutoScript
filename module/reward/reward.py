from module.base.button import ButtonGrid
from module.base.decorator import cached_property
from module.base.timer import Timer
from module.combat.assets import *
from module.logger import logger
from module.reward.assets import *
from module.ui.navbar import Navbar
from module.ui.page import *
from module.ui.ui import UI


class Reward(UI):
    def reward_receive(self, oil, coin, exp, skip_first_screenshot=True):
        """
        Args:
            oil (bool):
            coin (bool):
            exp (bool):
            skip_first_screenshot (bool):

        Returns:
            bool: If rewarded.

        Pages:
            in: page_reward
            out: page_reward, with info_bar if received
        """
        if not oil and not coin and not exp:
            return False

        logger.hr('Reward receive')
        logger.info(f'oil={oil}, coin={coin}')
        confirm_timer = Timer(1, count=3).start()
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if oil and self.appear_then_click(OIL, interval=60):
                confirm_timer.reset()
                continue
            if coin and self.appear_then_click(COIN, interval=60):
                confirm_timer.reset()
                continue
            if exp and self.appear_then_click(EXP, interval=60):
                confirm_timer.reset()
                continue

            # End
            if confirm_timer.reached():
                break

        logger.info('Reward receive end')
        return True

    def _reward_mission_collect(self, interval=1):
        """
        Streamline handling of mission rewards for
        both 'all' and 'weekly' pages

        Args:
            interval (int): Configure the interval for
                            assets involved

        Returns:
            bool, if encountered at least 1 GET_ITEMS_*
        """
        # Reset any existing interval for the following assets
        [self.interval_clear(asset) for asset in [GET_ITEMS_1, GET_ITEMS_2, MISSION_MULTI, MISSION_SINGLE, GET_SHIP]]

        # Basic timers for certain scenarios
        exit_timer = Timer(2)
        click_timer = Timer(1)
        timeout = Timer(10)
        exit_timer.start()
        timeout.start()

        reward = False
        while 1:
            self.device.screenshot()

            for button in [GET_ITEMS_1, GET_ITEMS_2]:
                if self.appear_then_click(button, offset=(30, 30), interval=interval):
                    exit_timer.reset()
                    timeout.reset()
                    reward = True
                    continue

            for button in [MISSION_MULTI, MISSION_SINGLE]:
                if not click_timer.reached():
                    continue
                if self.appear(button, offset=(0, 200), interval=interval) \
                        and button.match_appear_on(self.device.image):
                    self.device.click(button)
                    exit_timer.reset()
                    click_timer.reset()
                    timeout.reset()
                    continue

            if not self.appear(MISSION_CHECK):
                if self.appear_then_click(GET_SHIP, interval=interval):
                    exit_timer.reset()
                    click_timer.reset()
                    timeout.reset()
                    continue

            if self.handle_mission_popup_ack():
                exit_timer.reset()
                click_timer.reset()
                timeout.reset()
                continue

            if self.story_skip():
                exit_timer.reset()
                click_timer.reset()
                timeout.reset()
                continue

            if self.handle_popup_confirm('MISSION_REWARD'):
                exit_timer.reset()
                click_timer.reset()
                timeout.reset()
                continue

            # End
            if reward and exit_timer.reached():
                break
            if timeout.reached():
                logger.warning('Wait get items timeout.')
                break

        return reward

    def _reward_mission_all(self):
        """
        Collects all page mission rewards

        Returns:
            bool, if handled
        """
        self.reward_side_navbar_ensure(upper=1)

        if not self.appear(MISSION_MULTI) and \
                not self.appear(MISSION_SINGLE):
            return False

        # Uses default interval to account for
        # behavior differences and avoid
        # premature exit
        return self._reward_mission_collect()

    def _reward_mission_weekly(self):
        """
        Collects weekly page mission rewards

        Returns:
            bool, if handled
        """
        if not self.appear(MISSION_WEEKLY_RED_DOT):
            return False

        self.reward_side_navbar_ensure(upper=5)

        # Uses no interval to account for
        # behavior differences and avoid
        # premature exit
        return self._reward_mission_collect(interval=0)

    def reward_mission(self):
        """
        Returns:
            bool: If rewarded.

        Pages:
            in: page_main
            out: page_mission
        """
        logger.hr('Mission reward')
        if not self.appear(MISSION_NOTICE):
            logger.info('No mission reward')
            return False
        else:
            logger.info('Found mission reward notice')

        self.ui_goto(page_mission, skip_first_screenshot=True)

        # Handle all then weekly, key is both use
        # different intervals
        reward = self._reward_mission_all()
        reward |= self._reward_mission_weekly()

        return reward

    @cached_property
    def _reward_side_navbar(self):
        """
        side_navbar options:
           all.
           main.
           side.
           daily.
           weekly.
           event.
        """
        reward_side_navbar = ButtonGrid(
            origin=(21, 118), delta=(0, 94.5),
            button_shape=(60, 75), grid_shape=(1, 6),
            name='REWARD_SIDE_NAVBAR')

        return Navbar(grids=reward_side_navbar,
                      active_color=(247, 255, 173),
                      inactive_color=(140, 162, 181))

    def reward_side_navbar_ensure(self, upper=None, bottom=None):
        """
        Ensure able to transition to page
        Whether page has completely loaded is handled
        separately and optionally

        Args:
            upper (int):
                1  for all.
                2  for main.
                3  for side.
                4  for daily.
                5  for weekly.
                6  for event.
            bottom (int):
                6  for all.
                5  for main.
                4  for side.
                3  for daily.
                2  for weekly.
                1  for event.

        Returns:
            bool: if side_navbar set ensured
        """
        if self._reward_side_navbar.set(self, upper=upper, bottom=bottom):
            return True
        return False

    def run(self):
        """
        Pages:
            in: Any page
            out: page_main or page_mission, may have info_bar
        """
        self.ui_ensure(page_reward)
        self.reward_receive(
            oil=self.config.Reward_CollectOil,
            coin=self.config.Reward_CollectCoin,
            exp=self.config.Reward_CollectExp)
        if self.config.Reward_CollectMission:
            self.ui_goto(page_main)
            self.reward_mission()

        self.config.task_delay(success=True)
