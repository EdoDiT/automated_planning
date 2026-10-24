#ifndef PLANSYS2_INTERPLANETARY_MUSEUM_FAKE_ACTION_HPP
#define PLANSYS2_INTERPLANETARY_MUSEUM_FAKE_ACTION_HPP

#include <algorithm>
#include <chrono>
#include <memory>
#include <string>

#include "plansys2_executor/ActionExecutorClient.hpp"
#include "rclcpp/rclcpp.hpp"

class FakeAction : public plansys2::ActionExecutorClient
{
public:
  explicit FakeAction(const std::string & action_name)
  : plansys2::ActionExecutorClient(action_name, std::chrono::milliseconds(250)),
    action_name_(action_name)
  {
    set_parameter(rclcpp::Parameter("action_name", action_name));
  }

private:
  void do_work() override
  {
    if (progress_ < 1.0f) {
      progress_ = std::min(1.0f, progress_ + 0.25f);
      send_feedback(progress_, action_name_ + " running");
      return;
    }

    finish(true, 1.0, action_name_ + " completed");
    progress_ = 0.0f;
  }

  std::string action_name_;
  float progress_{0.0f};
};

#endif
