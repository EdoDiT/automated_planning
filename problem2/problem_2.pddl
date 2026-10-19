(define (problem martian_museum_2) (:domain interplanetary_museum_domain_2)
(:objects
    cryo-chamber - room
    hall_alpha - room
    stasis_lab - room
    curator - standard_curator
    biggie - tank_curator
    bee - drone_curator
    pod_1 - pod
    pod_2 - pod
    artifact_1 - artifact
    artifact_2 - artifact
    artifact_3 - artifact
    artifact_4 - artifact
    artifact_5 - artifact
    artifact_6 - artifact
    artifact_7 - artifact
    artifact_8 - artifact
    artifact_9 - artifact
    artifact_10 - artifact
    martian_artifact_1 - artifact
    martian_artifact_2 - artifact
    martian_artifact_3 - artifact
    martian_artifact_4 - artifact
    martian_artifact_5 - artifact
    martian_artifact_6 - artifact
    martian_artifact_7 - artifact
    martian_artifact_8 - artifact
    martian_artifact_9 - artifact
    martian_artifact_10 - artifact
)

(:init
    ;locations
    (is_freezing cryo-chamber)
    (is_vibration_free hall_alpha)
    (is_freezing stasis_lab)
    (is_vibration_free stasis_lab)
    (are_connected tunnel cryo-chamber)
    (are_connected tunnel hall_alpha)
    (are_connected tunnel hall_beta)
    (are_connected tunnel stasis_lab)
    (are_connected tunnel pod_pickup)
    ;curator
    (at curator tunnel)
    (is_sealed curator)
    (= (max_capacity curator) 1)
    (= (max_pod_capacity curator) 1)
    (= (capacity_available curator) 1)
    (= (pod_capacity_available curator) 1)
    (= (max_battery_level curator) 1000)
    (= (battery_level curator) 1000)
    (at biggie tunnel)
    (is_sealed biggie)
    (= (max_capacity biggie) 2)
    (= (max_pod_capacity biggie) 2)
    (= (capacity_available biggie) 2)
    (= (pod_capacity_available biggie) 2)
    (= (max_battery_level biggie) 2000)
    (= (battery_level biggie) 2000)
    (at bee tunnel)
    (is_unsealed bee)
    (= (max_capacity bee) 1)
    (= (max_pod_capacity bee) 1)
    (= (capacity_available bee) 1)
    (= (pod_capacity_available bee) 1)
    (= (max_battery_level bee) 1000)
    (= (battery_level bee) 1000)
    ;pods
    (at pod_1 pod_pickup)
    (at pod_2 pod_pickup)
    ;artifacts
    (at artifact_1 hall_alpha)
    (at artifact_2 hall_alpha)
    (at artifact_3 hall_alpha)
    (at artifact_4 hall_alpha)
    (at artifact_5 hall_alpha)
    (at artifact_6 hall_beta)
    (at artifact_7 hall_beta)
    (at artifact_8 hall_beta)
    (at artifact_9 hall_beta)
    (at artifact_10 hall_beta)
    (at martian_artifact_1 cryo-chamber)
    (at martian_artifact_2 cryo-chamber)
    (at martian_artifact_3 cryo-chamber)
    (at martian_artifact_4 stasis_lab)
    (at martian_artifact_5 stasis_lab)
    (at martian_artifact_6 stasis_lab)
    (at martian_artifact_7 stasis_lab)
    (at martian_artifact_8 stasis_lab)
    (at martian_artifact_9 stasis_lab)
    (at martian_artifact_10 stasis_lab)
)

(:goal (and
    (at artifact_1 cryo-chamber)
    (at artifact_2 stasis_lab)
    (at artifact_3 stasis_lab)
    (at artifact_4 cryo-chamber)
    (at artifact_5 hall_alpha)
    (at martian_artifact_1 stasis_lab)
    (at martian_artifact_2 stasis_lab)
    (at martian_artifact_3 stasis_lab)
))

;un-comment the following line if metric is needed
;(:metric minimize (???))
)
