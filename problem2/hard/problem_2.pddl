(define (problem martian_museum_2) (:domain interplanetary_museum_domain_2)
(:objects
    cryo_chamber - room
    hall_alpha - room
    stasis_lab - room
    curator - standard_curator
    biggie - tank_curator
    ;bee - drone_curator
    pod_1 - pod
    pod_2 - pod
    artifact_1 - artifact
    artifact_2 - artifact
    artifact_3 - artifact
    ;artifact_4 - artifact
    ;artifact_5 - artifact
    ;artifact_6 - artifact
    ;artifact_7 - artifact
    ;artifact_8 - artifact
    ;artifact_9 - artifact
    ;artifact_10 - artifact
    ;martian_artifact_1 - artifact
    ;martian_artifact_2 - artifact
    ;martian_artifact_3 - artifact
    ;martian_artifact_4 - artifact
    ;martian_artifact_5 - artifact
    ;martian_artifact_6 - artifact
    ;martian_artifact_7 - artifact
    ;martian_artifact_8 - artifact
    ;martian_artifact_9 - artifact
    ;martian_artifact_10 - artifact
)

(:init
    ;locations
    (is_freezing cryo_chamber)
    (is_vibration_free hall_alpha)
    (is_freezing stasis_lab)
    (is_vibration_free stasis_lab)
    (are_connected tunnel cryo_chamber)
    (are_connected cryo_chamber tunnel)
    (are_connected tunnel hall_alpha)
    (are_connected hall_alpha tunnel)
    (are_connected tunnel hall_beta)
    (are_connected hall_beta tunnel)
    (are_connected tunnel stasis_lab)
    (are_connected stasis_lab tunnel)
    (are_connected tunnel pod_pickup)
    (are_connected pod_pickup tunnel)
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
    ;(at bee tunnel)
    ;(is_unsealed bee)
    ;(= (max_capacity bee) 1)
    ;(= (max_pod_capacity bee) 1)
    ;(= (capacity_available bee) 1)
    ;(= (pod_capacity_available bee) 1)
    ;(= (max_battery_level bee) 1000)
    ;(= (battery_level bee) 1000)
    ;pods
    (at pod_1 pod_pickup)
    (at pod_2 pod_pickup)
    (pod_is_empty pod_1)
    (pod_is_empty pod_2)
    (pod_is_available pod_1)
    (pod_is_available pod_2)
    ;artifacts
    (at artifact_1 hall_alpha)
    (is_sturdy artifact_1)
    (at artifact_2 hall_alpha)
    (is_sensitive artifact_2)
    (is_thermosensitive artifact_2)
    (at artifact_3 hall_alpha)
    (is_sturdy artifact_3)
    ;(at artifact_4 hall_beta)
    ;(is_sensitive artifact_4)
    ;(is_seismic_sensitive artifact_4)
    ;(at artifact_5 hall_alpha)
    ;(is_sensitive artifact_5)
    ;(is_thermosensitive artifact_5)
    ;(at artifact_6 hall_beta)
    ;(is_sturdy artifact_6)
    ;(at artifact_7 hall_beta)
    ;(is_sensitive artifact_7)
    ;(is_seismic_sensitive artifact_7)
    ;(at artifact_8 hall_beta)
    ;(is_sensitive artifact_8)
    ;(is_seismic_sensitive artifact_8)
    ;(at artifact_9 hall_beta)
    ;(is_sensitive artifact_9)
    ;(is_thermo_and_seismic_sensitive artifact_9)
    ;(at artifact_10 hall_beta)
    ;(is_sensitive artifact_10)
    ;(is_thermo_and_seismic_sensitive artifact_10)
    ;(at martian_artifact_1 cryo_chamber)
    ;(is_sturdy martian_artifact_1)
    ;(at martian_artifact_2 cryo_chamber)
    ;(is_sensitive martian_artifact_2)
    ;(is_seismic_sensitive martian_artifact_2)
    ;(at martian_artifact_3 cryo_chamber)
    ;(is_sensitive martian_artifact_3)
    ;(is_thermo_and_seismic_sensitive martian_artifact_3)
    ;(at martian_artifact_4 stasis_lab)
    ;(is_sturdy martian_artifact_4)
    ;(at martian_artifact_5 stasis_lab)
    ;(is_sensitive martian_artifact_5)
    ;(is_thermosensitive martian_artifact_5)
    ;(at martian_artifact_6 stasis_lab)
    ;(is_sensitive martian_artifact_6)
    ;(is_thermosensitive martian_artifact_6)
    ;(at martian_artifact_7 stasis_lab)
    ;(is_sensitive martian_artifact_7)
    ;(is_seismic_sensitive martian_artifact_7)
    ;(at martian_artifact_8 stasis_lab)
    ;(is_sensitive martian_artifact_8)
    ;(is_seismic_sensitive martian_artifact_8)
    ;(at martian_artifact_9 stasis_lab)
    ;(is_sensitive martian_artifact_9)
    ;(is_thermo_and_seismic_sensitive martian_artifact_9)
    ;(at martian_artifact_10 stasis_lab)
    ;(is_sensitive martian_artifact_10)
    ;(is_thermosensitive martian_artifact_10)
    ;;earthquakes
    (= (seismic_counter) 0)
    (= (seismic_phase_duration) 20)
    (= (total_cost) 0)
    (is_not_seisming hall_beta)
    (is_not_seisming hall_alpha)
    (is_not_seisming stasis_lab)
    (is_not_seisming tunnel)
    (is_not_seisming pod_pickup)
    (is_not_seisming cryo_chamber)
)

(:goal (and
    (at artifact_1 cryo_chamber)
    (at artifact_2 stasis_lab)
    (at artifact_3 stasis_lab)
    ;(at artifact_4 hall_alpha)
    ;(at artifact_5 cryo_chamber)
    ;(at artifact_6 stasis_lab)
    ;(at artifact_7 stasis_lab)
    ;(at artifact_8 hall_alpha)
    ;(at artifact_9 stasis_lab)
    ;(at artifact_10 stasis_lab)
    ;(at martian_artifact_1 stasis_lab)
    ;(at martian_artifact_2 stasis_lab)
    ;(at martian_artifact_3 stasis_lab)
    ;(at martian_artifact_4 hall_alpha)
    ;(at martian_artifact_5 cryo_chamber)
    ;(at martian_artifact_6 cryo_chamber)
    ;(at martian_artifact_7 stasis_lab)
    ;(at martian_artifact_8 hall_alpha)
    ;(at martian_artifact_9 stasis_lab)
    ;(at martian_artifact_10 cryo_chamber)
))

(:metric minimize (total_cost))
)
