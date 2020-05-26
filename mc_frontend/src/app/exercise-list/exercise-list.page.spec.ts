import {CUSTOM_ELEMENTS_SCHEMA} from '@angular/core';
import {async, ComponentFixture, TestBed} from '@angular/core/testing';

import {ExerciseListPage} from './exercise-list.page';
import {HttpClientModule} from '@angular/common/http';
import {IonicStorageModule} from '@ionic/storage';
import {RouterModule} from '@angular/router';
import {TranslateTestingModule} from '../translate-testing/translate-testing.module';
import {FormsModule} from '@angular/forms';
import {IonicModule} from '@ionic/angular';
import {APP_BASE_HREF} from '@angular/common';
import {ExerciseType, MoodleExerciseType, SortingCategory, VocabularyCorpus} from '../models/enum';
import MockMC from '../models/mockMC';
import {ApplicationState} from '../models/applicationState';
import {ExerciseMC} from '../models/exerciseMC';
import Spy = jasmine.Spy;
import configMC from '../../configMC';
import {UpdateInfo} from '../models/updateInfo';

describe('ExerciseListPage', () => {
    let exerciseListPage: ExerciseListPage;
    let fixture: ComponentFixture<ExerciseListPage>;
    let getExerciseListSpy: Spy;

    beforeEach(async(() => {
        TestBed.configureTestingModule({
            declarations: [ExerciseListPage],
            imports: [
                FormsModule,
                HttpClientModule,
                IonicModule,
                IonicStorageModule.forRoot(),
                RouterModule.forRoot([]),
                TranslateTestingModule,
            ],
            providers: [
                {provide: APP_BASE_HREF, useValue: '/'},
            ],
            schemas: [CUSTOM_ELEMENTS_SCHEMA],
        })
            .compileComponents().then();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(ExerciseListPage);
        exerciseListPage = fixture.componentInstance;
        getExerciseListSpy = spyOn(exerciseListPage, 'getExerciseList').and.returnValue(Promise.resolve());
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(exerciseListPage).toBeTruthy();
        expect(exerciseListPage.getExerciseList).toHaveBeenCalled();
    });

    it('should filter exercises', () => {
        exerciseListPage.metadata.eid = 'test';
        exerciseListPage.availableExercises = [new ExerciseMC({eid: 'eid'})];
        exerciseListPage.filterExercises('test');
        expect(exerciseListPage.exercises.length).toBe(1);
    });

    it('should get a date string', () => {
        const dateString: string = exerciseListPage.getDateString(0);
        expect(dateString).toBe('1/1/1970');
    });

    it('should get the exercise list', (done) => {
        getExerciseListSpy.and.callThrough();
        const requestSpy: Spy = spyOn(exerciseListPage.helperService, 'makeGetRequest').and.callFake(() => Promise.reject());
        spyOn(exerciseListPage.storage, 'get').withArgs(configMC.localStorageKeyUpdateInfo).and.returnValue(
            Promise.resolve(JSON.stringify(new UpdateInfo({exerciseList: 0}))));
        exerciseListPage.getExerciseList().then(() => {
        }, () => {
            expect(requestSpy).toHaveBeenCalledTimes(1);
            exerciseListPage.vocService.currentReferenceVocabulary = VocabularyCorpus.agldt;
            exerciseListPage.helperService.applicationState.next(new ApplicationState({exerciseList: []}));
            requestSpy.and.returnValue(Promise.resolve([]));
            exerciseListPage.getExerciseList().then(() => {
                expect(exerciseListPage.availableExercises.length).toBe(0);
                exerciseListPage.helperService.applicationState.next(exerciseListPage.helperService.deepCopy(MockMC.applicationState));
                requestSpy.and.returnValue(Promise.resolve([new ExerciseMC()]));
                exerciseListPage.getExerciseList().then(() => {
                    expect(exerciseListPage.availableExercises.length).toBe(1);
                    done();
                });
            });
        });
    });

    it('should get the matching degree', () => {
        let degree: string = exerciseListPage.getMatchingDegree(new ExerciseMC({matching_degree: 20}));
        expect(degree).toBe('20');
        degree = exerciseListPage.getMatchingDegree(new ExerciseMC());
        expect(degree).toBeFalsy();
    });

    it('should show an exercise', (done) => {
        const requestSpy: Spy = spyOn(exerciseListPage.helperService, 'makeGetRequest').and.callFake(() => Promise.reject());
        spyOn(exerciseListPage.helperService, 'goToPreviewPage').and.returnValue(Promise.resolve(true));
        exerciseListPage.showExercise(new ExerciseMC()).then(() => {
            requestSpy.and.returnValue(Promise.resolve({}));
            exerciseListPage.showExercise(new ExerciseMC({exercise_type: MoodleExerciseType.markWords.toString()})).then(() => {
                expect(exerciseListPage.corpusService.exercise.type).toBe(ExerciseType.markWords);
                done();
            });
        });
    });

    it('should sort exercises', () => {
        let oldList: ExerciseMC[] = [new ExerciseMC({eid: 'a'}), new ExerciseMC({eid: 'b'})];
        exerciseListPage.exercises = [new ExerciseMC({eid: 'a'}), new ExerciseMC({eid: 'b'})];
        exerciseListPage.currentSortingCategory = SortingCategory.vocAsc;
        exerciseListPage.sortExercises();
        expect(exerciseListPage.exercises).toEqual(oldList);
        oldList = [new ExerciseMC({matching_degree: 1}), new ExerciseMC({matching_degree: 0}),
            new ExerciseMC({matching_degree: 0}), new ExerciseMC({matching_degree: 2})];
        exerciseListPage.exercises = [new ExerciseMC({matching_degree: 1}), new ExerciseMC({matching_degree: 0}),
            new ExerciseMC({matching_degree: 0}), new ExerciseMC({matching_degree: 2})];
        exerciseListPage.sortExercises();
        expect(exerciseListPage.exercises).not.toEqual(oldList);
        exerciseListPage.currentSortingCategory = SortingCategory.vocDesc;
        exerciseListPage.exercises.splice(0, 0, new ExerciseMC({matching_degree: 1}));
        exerciseListPage.sortExercises();
        expect(exerciseListPage.exercises).not.toEqual(oldList);
    });

    it('should toggle the vocabulary corpus display', () => {
        exerciseListPage.showVocabularyCorpus = false;
        exerciseListPage.toggleVocCorpus();
        expect(exerciseListPage.showVocabularyCorpus).toBe(true);
        exerciseListPage.toggleVocCorpus();
        expect(exerciseListPage.showVocabularyCorpus).toBe(false);
    });
});
