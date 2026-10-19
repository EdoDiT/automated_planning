(define (problem martian_museum_1) (:domain interplanetary_museum_domain_1)
(:objects
    cryo-chamber - location
    hall_alpha - location
    hall_beta - location
    stasis_lab - location
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
    ;curator
    (at curator tunnel)
    (is_sealed curator)
    (is_unloaded curator)
    (is_unpodded curator)
    ;pods
    (at pod_1 pod_pickup)
    (at pod_2 pod_pickup)
    ;artifacts
    (at artifact_1 hall_alpha)
    (at artifact_2 hall_alpha)
    (at artifact_3 hall_beta)
    (at artifact_4 hall_beta)
    (at artifact_5 hall_beta)
    (at martian_artifact_1 cryo-chamber)
    (at martian_artifact_2 cryo-chamber)
    (at martian_artifact_3 cryo-chamber)
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
