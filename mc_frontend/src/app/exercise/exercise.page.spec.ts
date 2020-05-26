import {CUSTOM_ELEMENTS_SCHEMA} from '@angular/core';
import {async, ComponentFixture, TestBed} from '@angular/core/testing';
import {ExercisePage} from './exercise.page';
import {HttpClientModule} from '@angular/common/http';
import {IonicStorageModule} from '@ionic/storage';
import {ActivatedRoute, RouterModule} from '@angular/router';
import {TranslateTestingModule} from '../translate-testing/translate-testing.module';
import {APP_BASE_HREF} from '@angular/common';
import {of} from 'rxjs';
import {ExerciseType, MoodleExerciseType} from '../models/enum';
import Spy = jasmine.Spy;
import configMC from '../../configMC';
import MockMC from '../models/mockMC';

describe('ExercisePage', () => {
    let exercisePage: ExercisePage;
    let fixture: ComponentFixture<ExercisePage>;
    let checkSpy: Spy;
    const activatedRouteMock: any = {queryParams: of({eid: 'eid', type: ExerciseType.cloze.toString()})};
    let getRequestSpy: Spy;
    let h5pSpy: Spy;

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
                {provide: ActivatedRoute, useValue: activatedRouteMock}
            ],
            schemas: [CUSTOM_ELEMENTS_SCHEMA],
        })
            .compileComponents().then();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(ExercisePage);
        exercisePage = fixture.componentInstance;
        h5pSpy = spyOn(exercisePage.exerciseService, 'initH5P').and.returnValue(Promise.resolve());
        checkSpy = spyOn(exercisePage.corpusService, 'checkAnnisResponse').and.callFake(() => Promise.reject());
        getRequestSpy = spyOn(exercisePage.helperService, 'makeGetRequest').and.returnValue(Promise.resolve(
            {exercise_type: MoodleExerciseType.cloze.toString()}));
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(exercisePage).toBeTruthy();
    });

    it('should be initialized', (done) => {
        const loadExerciseSpy: Spy = spyOn(exercisePage, 'loadExercise').and.returnValue(Promise.resolve());
        checkSpy.and.callFake(() => Promise.reject());
        exercisePage.ngOnInit().then(() => {
            expect(loadExerciseSpy).toHaveBeenCalledTimes(0);
            checkSpy.and.returnValue(Promise.resolve());
            exercisePage.ngOnInit().then(() => {
                done();
            });
        });
    });

    it('should load the exercise', (done) => {
        exercisePage.helperService.applicationState.next(exercisePage.helperService.deepCopy(MockMC.applicationState));
        exercisePage.loadExercise().then(() => {
            expect(exercisePage.corpusService.exercise.type).toBe(ExerciseType.cloze);
            getRequestSpy.and.returnValue(Promise.resolve({exercise_type: MoodleExerciseType.markWords.toString()}));
            exercisePage.loadExercise().then(() => {
                expect(h5pSpy).toHaveBeenCalledWith(configMC.excerciseTypePathMarkWords);
                getRequestSpy.and.callFake(() => Promise.reject());
                exercisePage.loadExercise().then(() => {
                }, () => {
                    activatedRouteMock.queryParams = of({eid: '', type: ExerciseType.matching.toString()});
                    exercisePage.loadExercise().then(() => {
                        expect(h5pSpy).toHaveBeenCalledWith(ExerciseType.matching.toString());
                        activatedRouteMock.queryParams = of({
                            eid: '',
                            type: exercisePage.exerciseService.vocListString
                        });
                        exercisePage.loadExercise().then(() => {
                            expect(h5pSpy).toHaveBeenCalledWith(exercisePage.exerciseService.fillBlanksString);
                            done();
                        });
                    });
                });
            });
        });
    });
});
