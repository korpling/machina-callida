import {CUSTOM_ELEMENTS_SCHEMA} from '@angular/core';
import {async, ComponentFixture, TestBed} from '@angular/core/testing';

import {ExerciseParametersPage} from './exercise-parameters.page';
import {HttpClientModule} from '@angular/common/http';
import {IonicStorageModule} from '@ionic/storage';
import {RouterModule} from '@angular/router';
import {TranslateTestingModule} from '../translate-testing/translate-testing.module';
import {FormsModule} from '@angular/forms';
import {APP_BASE_HREF} from '@angular/common';
import {TextRange} from '../models/textRange';
import {ReplaySubject} from 'rxjs';
import configMC from '../../configMC';
import {ExerciseType, PartOfSpeechValue} from '../models/enum';
import {ToastController} from '@ionic/angular';
import {QueryMC} from '../models/queryMC';
import {PhenomenonMapContent} from '../models/phenomenonMap';
import Spy = jasmine.Spy;
import MockMC from '../models/mockMC';
import {ExerciseForm, Phenomenon} from '../../../openapi';

describe('ExerciseParametersPage', () => {
    let exerciseParametersPage: ExerciseParametersPage;
    let fixture: ComponentFixture<ExerciseParametersPage>;

    beforeEach(async(() => {
        TestBed.configureTestingModule({
            declarations: [ExerciseParametersPage],
            imports: [
                FormsModule,
                HttpClientModule,
                IonicStorageModule.forRoot(),
                RouterModule.forRoot([]),
                TranslateTestingModule,
            ],
            providers: [
                {provide: APP_BASE_HREF, useValue: '/'},
                {provide: ToastController, useValue: MockMC.toastController},
            ],
            schemas: [CUSTOM_ELEMENTS_SCHEMA],
        })
            .compileComponents().then();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(ExerciseParametersPage);
        exerciseParametersPage = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(exerciseParametersPage).toBeTruthy();
    });

    it('should generate an exercise', (done) => {
        exerciseParametersPage.corpusService.annisResponse = {solutions: []};
        exerciseParametersPage.helperService.applicationState.next(exerciseParametersPage.helperService.deepCopy(MockMC.applicationState));
        exerciseParametersPage.corpusService.initCurrentCorpus().then(async () => {
            exerciseParametersPage.corpusService.currentTextRange = new ReplaySubject<TextRange>(1);
            exerciseParametersPage.corpusService.currentTextRange.next(new TextRange({start: [], end: []}));
            const h5pSpy: Spy = spyOn(exerciseParametersPage, 'getH5Pexercise').and.returnValue(Promise.resolve());
            await exerciseParametersPage.generateExercise();
            expect(exerciseParametersPage.corpusService.annisResponse.solutions).toBeFalsy();
            expect(h5pSpy).toHaveBeenCalledTimes(1);
            configMC.maxTextLength = 1;
            exerciseParametersPage.corpusService.currentText = 'text';
            exerciseParametersPage.generateExercise().then(() => {
            }, () => {
                expect(h5pSpy).toHaveBeenCalledTimes(1);
                configMC.maxTextLength = 0;
                exerciseParametersPage.corpusService.exercise.queryItems[0].phenomenon = Phenomenon.Lemma;
                exerciseParametersPage.corpusService.exercise.type = ExerciseType.matching;
                exerciseParametersPage.corpusService.exercise.queryItems.push(new QueryMC({values: []}));
                exerciseParametersPage.generateExercise().then(() => {
                }, () => {
                    expect(h5pSpy).toHaveBeenCalledTimes(1);
                    done();
                });
            });
        });
    });

    it('should get a display value', () => {
        const pmc: PhenomenonMapContent = exerciseParametersPage.corpusService.phenomenonMap[Phenomenon.Lemma];
        pmc.translationValues = {key: 'value'};
        pmc.specificValues = {key: 1};
        const key = 'key';
        let displayValue: string = exerciseParametersPage.getDisplayValue(new QueryMC({phenomenon: Phenomenon.Lemma}), key);
        expect(displayValue.length).toBe(9);
        exerciseParametersPage.corpusService.exercise.type = ExerciseType.matching;
        exerciseParametersPage.corpusService.annisResponse = {
            frequency_analysis: [{values: [PartOfSpeechValue.adjective.toString(), key], count: 10}]
        };
        displayValue = exerciseParametersPage.getDisplayValue(new QueryMC({phenomenon: Phenomenon.Lemma}), key, 1);
        expect(displayValue.length).toBe(10);
        exerciseParametersPage.corpusService.annisResponse.frequency_analysis[0] = {
            phenomena: [Phenomenon.Lemma],
            values: [key],
            count: 100
        };
        exerciseParametersPage.corpusService.annisResponse.frequency_analysis.push(
            exerciseParametersPage.corpusService.annisResponse.frequency_analysis[0]);
        displayValue = exerciseParametersPage.getDisplayValue(new QueryMC({phenomenon: Phenomenon.Lemma}), key, 0);
        expect(displayValue.length).toBe(11);
    });

    it('should get exercise data', (done) => {
        exerciseParametersPage.helperService.applicationState.next(exerciseParametersPage.helperService.deepCopy(MockMC.applicationState));
        exerciseParametersPage.corpusService.initCurrentCorpus().then(async () => {
            exerciseParametersPage.corpusService.currentTextRange = new ReplaySubject<TextRange>(1);
            exerciseParametersPage.corpusService.currentTextRange.next(new TextRange({start: ['', ''], end: ['', '']}));
            const h5pSpy: Spy = spyOn(exerciseParametersPage, 'getH5Pexercise').and.returnValue(Promise.resolve());
            const kwicSpy: Spy = spyOn(exerciseParametersPage, 'getKwicExercise').and.returnValue(Promise.resolve());
            exerciseParametersPage.corpusService.exercise.type = ExerciseType.kwic;
            await exerciseParametersPage.getExerciseData();
            expect(kwicSpy).toHaveBeenCalledTimes(1);
            exerciseParametersPage.corpusService.exercise.type = ExerciseType.markWords;
            const pmc: PhenomenonMapContent = exerciseParametersPage.corpusService.phenomenonMap[Phenomenon.Upostag];
            pmc.translationValues = {};
            pmc.translationValues[PartOfSpeechValue.adjective.toString()] = '';
            await exerciseParametersPage.getExerciseData();
            expect(h5pSpy).toHaveBeenCalledTimes(1);
            done();
        });
    });

    it('should get a H5P exercise', (done) => {
        const requestSpy: Spy = spyOn(exerciseParametersPage.helperService, 'makePostRequest').and.returnValue(Promise.resolve({}));
        const navSpy: Spy = spyOn(exerciseParametersPage.helperService, 'goToPage').and.returnValue(Promise.resolve(true));
        exerciseParametersPage.corpusService.annisResponse = {};
        exerciseParametersPage.helperService.applicationState.next(exerciseParametersPage.helperService.deepCopy(MockMC.applicationState));
        const ef: ExerciseForm = {instructions: '', search_values: '', type: '', urn: ''};
        exerciseParametersPage.getH5Pexercise(ef).then(() => {
            expect(navSpy).toHaveBeenCalledTimes(1);
            requestSpy.and.callFake(() => Promise.reject());
            exerciseParametersPage.getH5Pexercise(ef).then(() => {
            }, () => {
                expect(navSpy).toHaveBeenCalledTimes(1);
                done();
            });
        });
    });

    it('should get a KWIC exercise', (done) => {
        const navSpy: Spy = spyOn(exerciseParametersPage.helperService, 'goToPage').and.returnValue(Promise.resolve(true));
        const requestSpy: Spy = spyOn(exerciseParametersPage.helperService, 'makePostRequest').and.returnValue(Promise.resolve('svg'));
        exerciseParametersPage.getKwicExercise('').then(() => {
            expect(exerciseParametersPage.exerciseService.kwicGraphs.length).toBe(3);
            expect(navSpy).toHaveBeenCalledTimes(1);
            requestSpy.and.callFake(() => Promise.reject());
            exerciseParametersPage.getKwicExercise('').then(() => {
            }, () => {
                expect(navSpy).toHaveBeenCalledTimes(1);
                done();
            });
        });
    });
});
