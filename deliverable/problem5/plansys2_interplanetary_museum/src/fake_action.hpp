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
  FakeAction(const std::string & action_name, std::chrono::seconds duration)
  : plansys2::ActionExecutorClient(action_name, std::chrono::milliseconds(250)),
    action_name_(action_name),
    duration_(duration)
  {
    set_parameter(rclcpp::Parameter("action_name", action_name));
  }

private:
  void do_work() override
  {
    elapsed_ += tick_;

    if (elapsed_ < duration_) {
      const auto progress = std::min(
        1.0,
        static_cast<double>(elapsed_.count()) /
        std::chrono::duration_cast<std::chrono::milliseconds>(duration_).count());
      send_feedback(progress, action_name_ + " running");
      return;
    }

    finish(true, 1.0, action_name_ + " completed");
    elapsed_ = std::chrono::milliseconds::zero();
  }

  std::string action_name_;
  const std::chrono::seconds duration_;
  std::chrono::milliseconds elapsed_{0};
  static constexpr std::chrono::milliseconds tick_{250};
};

#endif
