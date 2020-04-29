import {TestBed} from '@angular/core/testing';

import {ExerciseService} from './exercise.service';
import {APP_BASE_HREF} from '@angular/common';
import configMC from '../configMC';
import {HttpClientTestingModule} from '@angular/common/http/testing';
import {IonicStorageModule} from '@ionic/storage';
import {TranslateTestingModule} from './translate-testing/translate-testing.module';

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

    it('should initialize H5P', (done) => {
        let h5pCalled = false;
        // tslint:disable-next-line:no-string-literal
        window['H5P'] = {
            jQuery: () => {
                h5pCalled = true;
                return {
                    empty: () => {
                        return {
                            h5p: (selector: string) => {
                            }
                        };
                    }
                };
            }, off: () => {
            }
        };
        exerciseService.initH5P('').then(() => {
            expect(h5pCalled).toBe(true);
            // load script, restore old H5P variable
            const script: HTMLScriptElement = document.createElement('script');
            script.type = 'text/javascript';
            script.src = configMC.h5pAssetFilePath;
            document.querySelector('head').appendChild(script);
            done();
        });
    });
});
