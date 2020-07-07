import {CUSTOM_ELEMENTS_SCHEMA} from '@angular/core';
import {async, ComponentFixture, TestBed} from '@angular/core/testing';
import {ExercisePage} from './exercise.page';
import {HttpClientModule} from '@angular/common/http';
import {IonicStorageModule} from '@ionic/storage';
import {ActivatedRoute, RouterModule} from '@angular/router';
import {TranslateTestingModule} from '../translate-testing/translate-testing.module';
import {APP_BASE_HREF} from '@angular/common';
import {of} from 'rxjs';
import Spy = jasmine.Spy;

describe('ExercisePage', () => {
    let exercisePage: ExercisePage;
    let fixture: ComponentFixture<ExercisePage>;
    let checkSpy: Spy;
    let loadExerciseSpy: Spy;

    beforeEach(async(() => {
        TestBed.configureTestingModule({
            declarations: [ExercisePage],
            imports: [
                HttpClientModule,
                IonicStorageModule.forRoot(),
                RouterModule.forRoot([]),
                TranslateTestingModule,
            ],
            providers: [
                {provide: APP_BASE_HREF, useValue: '/'},
                {provide: ActivatedRoute, useValue: {queryParams: of({})}},
            ],
            schemas: [CUSTOM_ELEMENTS_SCHEMA],
        })
            .compileComponents().then();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(ExercisePage);
        exercisePage = fixture.componentInstance;
        checkSpy = spyOn(exercisePage.corpusService, 'checkAnnisResponse').and.returnValue(Promise.resolve());
        loadExerciseSpy = spyOn(exercisePage.exerciseService, 'loadExercise').and.returnValue(Promise.resolve());
        fixture.detectChanges();
    });

    it('should create', (done) => {
        expect(exercisePage).toBeTruthy();
        loadExerciseSpy.and.callFake(() => Promise.reject());
        exercisePage.ngOnInit().then(() => {
            expect(loadExerciseSpy).toHaveBeenCalledTimes(2);
            checkSpy.and.callFake(() => Promise.reject());
            exercisePage.ngOnInit().then(() => {
                expect(loadExerciseSpy).toHaveBeenCalledTimes(2);
                done();
            });
        });
    });

    it('should load an exercise', (done) => {
        loadExerciseSpy.and.returnValue(Promise.resolve());
        exercisePage.initExercise().then(() => {
            loadExerciseSpy.and.callFake(() => Promise.reject());
            exercisePage.initExercise().then(() => {
            }, () => {
                expect(loadExerciseSpy).toHaveBeenCalledTimes(3);
                done();
            });
        });
    });
});
