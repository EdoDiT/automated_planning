(define (problem martian_museum_1) (:domain interplanetary_museum_domain_1)
(:objects
    cryo-chamber - room
    hall_alpha - room
    hall_beta - room
    stasis_lab - room
    curator - standard_curator
    pod_1 - pod
    pod_2 - pod
    artifact_1 - artifact
    artifact_2 - artifact
    artifact_3 - artifact
    artifact_4 - artifact
    artifact_5 - artifact
    martian_artifact_1 - artifact
    martian_artifact_2 - artifact
    martian_artifact_3 - artifact    
)

(:init
    ;locations
    (is_freezing cryo-chamber)
    (is_vibration_free hall_alpha)
    (is_freezing stasis_lab)
    (is_vibration_free stasis_lab)
    (connected cryo-chamber)
    (connected hall_alpha)
    (connected hall_beta)
    (connected stasis_lab)
    (connected pod_pickup)
    (is_not_seisming cryo-chamber)
    (is_not_seisming hall_alpha)
    (is_not_seisming hall_beta)
    (is_not_seisming stasis_lab)
    (is_not_seisming pod_pickup)
    (is_not_seisming tunnel)
    ;curator
    (at curator tunnel)
    (is_sealed curator)
    (is_unloaded curator)
    (is_unpodded curator)
    ;pods
    (at pod_1 pod_pickup)
    (at pod_2 pod_pickup)
    (pod_is_available pod_1)
    (pod_is_available pod_2)
    (pod_is_empty pod_1)
    (pod_is_empty pod_2)
    ;artifacts
    (at artifact_1 hall_alpha)
    (is_sensitive artifact_1)
    (is_thermosensitive artifact_1)
    (at artifact_2 hall_alpha)
    (is_sturdy artifact_2)
    (at artifact_3 hall_beta)
    (is_sturdy artifact_3)
    (at artifact_4 hall_beta)
    (is_sensitive artifact_4)
    (is_thermo_and_seismic_sensitive artifact_4)
    (at artifact_5 hall_beta)
    (is_sensitive artifact_5)
    (is_seismic_sensitive artifact_5)
    (at martian_artifact_1 cryo-chamber)
    (is_sturdy martian_artifact_1)
    (at martian_artifact_2 cryo-chamber)
    (is_sensitive martian_artifact_2)
    (is_thermosensitive martian_artifact_2)
    (at martian_artifact_3 cryo-chamber)
    (is_sensitive martian_artifact_3)
    (is_thermo_and_seismic_sensitive martian_artifact_3)
)

(:goal (and
    (at artifact_1 cryo-chamber)
    (at artifact_2 stasis_lab)
    (at artifact_3 stasis_lab)
    (at artifact_4 stasis_lab)
    (at artifact_5 hall_alpha)
    (at martian_artifact_1 stasis_lab)
    (at martian_artifact_2 stasis_lab)
    (at martian_artifact_3 stasis_lab)
    (is_safe artifact_1)
    (is_safe artifact_2)
    (is_safe artifact_3)
    (is_safe artifact_4)
    (is_safe artifact_5)
    (is_safe martian_artifact_1)
    (is_safe martian_artifact_2)
    (is_safe martian_artifact_3)
))

;un-comment the following line if metric is needed
;(:metric minimize (???))
)
