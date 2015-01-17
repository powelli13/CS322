#lang racket
;; Geoffrey Matthews
;; 2013
;; Edited by Isaac Powell for csci322
;; Each planet runs within a thread

(require racket/gui)

;; Small 2d vector library for the Newtonian physics
(define (x v) (vector-ref v 0))
(define (y v) (vector-ref v 1))
(define (x! v value) (vector-set! v 0 value))
(define (y! v value) (vector-set! v 1 value))
(define (v* v value) (vector-map (lambda (x) (* x value)) v))
(define (v+ v w) (vector-map + v w))
(define (v- v w) (vector-map - v w))
(define (v-zero! v) (vector-map! (lambda (x) 0) v))
(define (v-dot v w) (let ((vw (vector-map * v w))) (+ (x vw) (y vw))))
(define (v-mag v) (sqrt (v-dot v v)))

;; vector of threads
(define threads (list))


;; Planet object
(define planet%
  (class object%
    (public m p v calculate-force move draw)
    (init-field (mass 1)
                (position (vector 0 0 ))
                (velocity (vector 0 0 ))
                (force (vector 0 0 )))
    (define (m) mass)
    (define (p) position)
    (define (v) velocity)
    ;; Use Newton's law of gravitation.
    ;; I assume the gravitational constant is one
    (define (calculate-force pl)
      (v-zero! force)
      (for-each (lambda (other-planet)
                  (when (not (equal? this other-planet))
                    (let* ((direction (v- (send other-planet p) position))
                           (dist (max 1 (v-mag direction)))
                           (other-mass (send other-planet m))
                           (new-force (v* direction (/ (* mass other-mass) (* dist dist))))
                          )
                      (vector-map! + force new-force))))
                pl)
      )
    ;; Simple Euler integration of acceleration and velocity
    (define (move) 
      (let ((acc (v* force (/ 1.0 mass))))
        (vector-map! + velocity acc)
        (vector-map! + position velocity)))
    ;; Draw a circle 
    (define (draw dc) 
      (send dc set-brush brush)
      (send dc set-pen pen)
      (send dc draw-ellipse (x position) (y position) radius radius ))
    ;; Initialize 
    ;(x! velocity (* 2 (- 0.5 (random))))
    ;(y! velocity (* 2 (- 0.5 (random))))
    (set! mass (+ 1 (* 10 (random))))
    (define radius (* 5 (sqrt mass)))
    (define color 
      (let* ((r (random))
             (b (real->floating-point-bytes r 4)))
        (make-object color% (bytes-ref b 0) (bytes-ref b 1) (bytes-ref b 2) )))
    (define brush (make-object brush% color))
    (define pen (make-object pen% color))
    ;; Don't forget the super-new!
    (super-new)
    ))
;; Abstract the list-handling for a list of planets
(define planet-container%
  (class object%
    ;;(public add-planet calculate-force move draw get-planets reset)
    (public add-planet draw get-planets reset)
    (init-field (planets '()))
    (define (get-planets) planets)
    (define (reset) (set! planets '()))
    (define (add-planet planet)
      (set! planets (cons planet planets))
      (set! threads (cons (thread 
                           (lambda ()
                             (let loop()
                               (sleep 0.1)
                               (send planet calculate-force planets)
                               (send planet move)
                             (loop)))) threads)))
    (define (draw dc)
      (for-each (lambda (planet)
                  (send planet draw dc))
                planets))
    (super-new)
    )
  )
(define planet-container (new planet-container%))
    
;; The GUI
;; augmented to kill thread on close
(define my-frame%
  (class frame%
    (define (on-close)
      (lambda (b e)
          (for-each (lambda (t)
            (kill-thread t)) threads)
          (kill-thread animate)))
    (augment on-close)
    (super-new)))

(define frame (new my-frame% 
                   (label "Planets")
                   (min-width 120)
                   (min-height 80)
                   ))
(send frame create-status-line)
(send frame show #t)

(define h-panel
  (new horizontal-panel%
       (parent frame)
       (stretchable-height #f)
       (style '(border))
       (border 2)))

(define run-checkbox
  (new check-box%
       (parent h-panel)
       (label "Run animation")
  (callback
   (lambda (b e)
     (cond ((thread-running? animate)
            (thread-suspend animate)
            (for-each (lambda (t) 
             (thread-suspend t)) threads))
     (else (thread-resume animate)
           (for-each (lambda (t)
              (thread-resume t)) threads)))))))

(define reset-button
  (new button%
       (parent h-panel)
       (label "Reset")
       (callback
        (lambda (b e)
          (send planet-container reset)
          (for-each (lambda (t)
                      (kill-thread t)) threads)
          (set! threads '())))))

(define my-canvas%
  (class canvas%
    (override on-paint on-event)
    
    (define (on-paint)
      (let ((dc (send this get-dc))
            (w (send this get-width))
            (h (send this get-height)))
        (send dc clear)
        (send planet-container draw dc)
        ))
    (define (on-event event)
      (when (send event button-down?)
        (let ((x (send event get-x))
              (y (send event get-y)))
          (send frame set-status-text (format "Mouse at ~a ~a" x y))
          (send planet-container add-planet (new planet% (position (vector x y))))
          (send this refresh)))
      )
    (super-new)
    (send (send this get-dc) set-background (make-object color% 8 8 64))
    ))

(define canvas
  (new my-canvas%
       (parent frame)
       (style '(border))
       (min-width 640)
       (min-height 480)))

;; loop for planet animator thread
(define animate
  (thread
   (lambda ()
     (let loop ()
       (sleep .1)
         (send canvas refresh)
  (loop)))))
