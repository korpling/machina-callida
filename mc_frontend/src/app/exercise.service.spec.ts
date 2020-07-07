import {TestBed} from '@angular/core/testing';

import {ExerciseService} from './exercise.service';
import {APP_BASE_HREF} from '@angular/common';
import {HttpClientTestingModule} from '@angular/common/http/testing';
import {IonicStorageModule} from '@ionic/storage';
import {TranslateTestingModule} from './translate-testing/translate-testing.module';
import {ExercisePart} from './models/exercisePart';
import MockMC from './models/mockMC';
import {ApplicationState} from './models/applicationState';
import {AnnisResponse} from '../../openapi';
import {ExerciseType, MoodleExerciseType} from './models/enum';
import {ExerciseParams} from './models/exerciseParams';
import Spy = jasmine.Spy;
import configMC from '../configMC';

declare var H5PStandalone: any;

describe('ExerciseService', () => {
    let exerciseService: ExerciseService;
    beforeEach(() => {
        TestBed.configureTestingModule({
            imports: [
                HttpClientTestingModule,
                IonicStorageModule.forRoot(),
                TranslateTestingModule,
            ],
            providers: [
                {provide: APP_BASE_HREF, useValue: '/'},
            ],
        });
        exerciseService = TestBed.inject(ExerciseService);
    });

    it('should be created', () => {
        expect(exerciseService).toBeTruthy();
    });

    it('should create a GUID', () => {
        const guid: string = exerciseService.createGuid();
        expect(guid.length).toBe(36);
    });

    it('should create a new H5P standalone instance', (done) => {
        let h5pCreated = false;

        class MockH5P extends Promise<void> {
            constructor(el, h5pLocation, options, displayOptions) {
                super((resolve) => {
                    h5pCreated = true;
                    return resolve();
                });
            }
        }

        spyOn(H5PStandalone, 'H5P').and.returnValue(MockH5P);
        const promise: any = exerciseService.createH5Pstandalone(null, '', null, null);
        promise.resolve().then(() => {
            expect(h5pCreated).toBe(true);
            done();
        });
    });

    it('should get H5P elements', () => {
        expect(exerciseService.getH5Pelements('')).toBeFalsy();
        const iframe: HTMLIFrameElement = MockMC.addIframe(exerciseService.h5pIframeString);
        const element: HTMLElement = exerciseService.getH5Pelements('body');
        expect(element).toBeTruthy();
        const nodeList: NodeList = exerciseService.getH5Pelements('head', true);
        expect(nodeList.length).toBe(1);
        iframe.parentNode.removeChild(iframe);
    });

    it('should initialize H5P', (done) => {
        let h5pCalled = false;
        spyOn(exerciseService, 'createH5Pstandalone').and.callFake(() => new Promise(resolve => {
            h5pCalled = true;
            return resolve();
        }));
        exerciseService.initH5P('', false).then(() => {
            expect(h5pCalled).toBe(true);
            done();
        });
    });

    it('should load an exercise', (done) => {
        const ar: AnnisResponse = {exercise_type: MoodleExerciseType.cloze.toString()};
        const getSpy: Spy = spyOn(exerciseService.helperService, 'makeGetRequest').and.returnValue(Promise.resolve(ar));
        const initSpy: Spy = spyOn(exerciseService, 'initH5P').and.returnValue(Promise.resolve());
        exerciseService.helperService.applicationState.next(
            exerciseService.helperService.deepCopy(MockMC.applicationState) as ApplicationState);
        let ep: ExerciseParams = {eid: 'eid'};
        exerciseService.loadExercise(ep).then(() => {
            expect(initSpy).toHaveBeenCalledTimes(1);
            getSpy.and.callFake(() => Promise.reject());
            exerciseService.loadExercise(ep).then(() => {
            }, () => {
                expect(initSpy).toHaveBeenCalledTimes(1);
                ep = {file: '', type: ''};
                exerciseService.loadExercise(ep).then(() => {
                    ep = {file: '', type: exerciseService.vocListString};
                    exerciseService.loadExercise(ep).then(() => {
                        expect(initSpy).toHaveBeenCalledTimes(3);
                        done();
                    });
                });
            });
        });
    });

    it('should load H5P', (done) => {
        const initSpy: Spy = spyOn(exerciseService, 'initH5P').and.returnValue(Promise.resolve());
        exerciseService.corpusService.exercise.type = ExerciseType.markWords;
        exerciseService.loadH5P('').then(() => {
            expect(initSpy).toHaveBeenCalledTimes(1);
            done();
        });
    });

    it('should set H5P event handlers', (done) => {
        const iframe: HTMLIFrameElement = MockMC.addIframe(exerciseService.h5pIframeString);
        const listElement: HTMLElement = document.createElement('ul');
        const embedElement: HTMLElement = document.createElement('li');
        embedElement.classList.add(exerciseService.embedButtonString.slice(1));
        listElement.appendChild(embedElement);
        iframe.contentWindow.document.body.appendChild(listElement);
        const input: HTMLInputElement = document.createElement('input');
        input.classList.add(exerciseService.embedSizeInputString.slice(1));
        iframe.contentWindow.document.body.appendChild(input);
        const updateSpy: Spy = spyOn(exerciseService, 'updateEmbedUrl');
        exerciseService.setH5PeventHandlers();
        embedElement.click();
        setTimeout(() => {
            expect(updateSpy).toHaveBeenCalledTimes(1);
            iframe.parentElement.removeChild(iframe);
            done();
        }, 500);
    });

    it('should set the current exercise index', () => {
        expect(exerciseService.currentExercisePartIndex).toBeFalsy();
        const exerciseName = 'ex';
        exerciseService.currentExerciseParts = [new ExercisePart({startIndex: 0}),
            new ExercisePart({startIndex: 2, exercises: ['', exerciseName]}), new ExercisePart({startIndex: 4})];
        exerciseService.currentExerciseIndex = 3;
        expect(exerciseService.currentExercisePartIndex).toBe(1);
        expect(exerciseService.currentExerciseIndex).toBe(3);
        expect(exerciseService.currentExerciseName).toBe(exerciseName);
        exerciseService.currentExerciseIndex = 1;
        expect(exerciseService.currentExerciseName).toBeFalsy();
    });

    it('should set the H5P URL', () => {
        const url = 'url';
        exerciseService.setH5Purl(url);
        expect(window.localStorage.getItem(configMC.localStorageKeyH5P)).toBe(url);
    });

    it('should update the embed URL', () => {
        const iframe: HTMLIFrameElement = MockMC.addIframe(exerciseService.h5pIframeString);
        const textarea: HTMLTextAreaElement = document.createElement('textarea');
        textarea.classList.add(exerciseService.embedTextAreaString.slice(1));
        const inputs: HTMLInputElement[] = [document.createElement('input'), document.createElement('input')];
        inputs.forEach((input) => {
            input.classList.add(exerciseService.embedSizeInputString.slice(1));
            iframe.contentWindow.document.body.appendChild(input);
        });
        iframe.contentWindow.document.body.appendChild(textarea);
        exerciseService.corpusService.annisResponse = {exercise_type: MoodleExerciseType.cloze.toString()};
        exerciseService.updateEmbedUrl();
        expect(textarea.innerHTML).toBeTruthy();
        iframe.parentElement.removeChild(iframe);
    });
});
